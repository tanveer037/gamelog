from decimal import Decimal

import pytest
from model_bakery import baker

from tracker.models import Game, GameSession, Platform


@pytest.mark.django_db
class TestGameList:
    def test_returns_200(self, api_client):
        baker.make(Game, _quantity=3)

        response = api_client.get('/tracker/games/')

        assert response.status_code == 200
        assert response.data['count'] == 3

    def test_query_count_is_flat(self, api_client, django_assert_num_queries):
        baker.make(Game, _quantity=5)

        with django_assert_num_queries(3):
            api_client.get('/tracker/games/')


@pytest.mark.django_db
class TestCreateGame:
    def test_valid_payload_returns_201(self, api_client):
        platform = baker.make(Platform)

        response = api_client.post('/tracker/games/', {
            'title': 'Hollow Knight',
            'platform': platform.id,
        }, format='json')

        assert response.status_code == 201
        assert response.data['title'] == 'Hollow Knight'

    @pytest.mark.parametrize('payload, expected_field', [
        ({},                                'title'),
        ({'title': 'X', 'rating': 9},       'rating'),
        ({'title': 'X', 'rating': 0},       'rating'),
        ({'title': 'X', 'status': 'Z'},     'status'),
    ], ids=[
        'missing title',
        'rating above five',
        'rating below one',
        'invalid status choice',
    ])
    def test_invalid_payload_returns_400(self, api_client, payload, expected_field):
        platform = baker.make(Platform)

        response = api_client.post('/tracker/games/', {
            'platform': platform.id,
            **payload,
        }, format='json')

        assert response.status_code == 400
        assert expected_field in response.data

    def test_nonexistent_platform_returns_400(self, api_client):
        response = api_client.post('/tracker/games/', {
            'title': 'X',
            'platform': 999,
        }, format='json')

        assert response.status_code == 400
        assert 'platform' in response.data


@pytest.mark.django_db
class TestTotalHours:
    def test_sums_sessions_and_untracked(self, api_client):
        game = baker.make(Game, untracked_hours=Decimal('100.00'))
        baker.make(GameSession, game=game, duration_hours=Decimal('2.50'))
        baker.make(GameSession, game=game, duration_hours=Decimal('1.50'))

        response = api_client.get(f'/tracker/games/{game.id}/')

        assert response.data['total_hours'] == '104.00'

    def test_is_zero_when_nothing_logged(self, api_client):
        game = baker.make(Game)

        response = api_client.get(f'/tracker/games/{game.id}/')

        assert response.data['total_hours'] == '0.00'

    def test_patching_untracked_hours_updates_total(self, api_client):
        game = baker.make(Game, untracked_hours=Decimal('0.00'))

        response = api_client.patch(f'/tracker/games/{game.id}/', {
            'untracked_hours': '50.00',
        }, format='json')

        assert response.status_code == 200
        assert response.data['total_hours'] == '50.00'
