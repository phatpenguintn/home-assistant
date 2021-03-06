"""Fixtures for Hass.io."""
import os
from unittest.mock import patch, Mock

import pytest

from homeassistant.core import CoreState
from homeassistant.setup import async_setup_component
from homeassistant.components.hassio.handler import HassIO, HassioAPIError

from tests.common import mock_coro
from . import API_PASSWORD, HASSIO_TOKEN


@pytest.fixture
def hassio_env():
    """Fixture to inject hassio env."""
    with patch.dict(os.environ, {'HASSIO': "127.0.0.1"}), \
            patch('homeassistant.components.hassio.HassIO.is_connected',
                  Mock(return_value=mock_coro(
                    {"result": "ok", "data": {}}))), \
            patch.dict(os.environ, {'HASSIO_TOKEN': "123456"}), \
            patch('homeassistant.components.hassio.HassIO.'
                  'get_homeassistant_info',
                  Mock(side_effect=HassioAPIError())):
        yield


@pytest.fixture
def hassio_client(hassio_env, hass, aiohttp_client, legacy_auth):
    """Create mock hassio http client."""
    with patch('homeassistant.components.hassio.HassIO.update_hass_api',
               Mock(return_value=mock_coro({"result": "ok"}))), \
            patch('homeassistant.components.hassio.HassIO.'
                  'get_homeassistant_info',
                  Mock(side_effect=HassioAPIError())):
        hass.state = CoreState.starting
        hass.loop.run_until_complete(async_setup_component(hass, 'hassio', {
            'http': {
                'api_password': API_PASSWORD
            }
        }))
    yield hass.loop.run_until_complete(aiohttp_client(hass.http.app))


@pytest.fixture
def hassio_handler(hass, aioclient_mock):
    """Create mock hassio handler."""
    websession = hass.helpers.aiohttp_client.async_get_clientsession()

    with patch.dict(os.environ, {'HASSIO_TOKEN': HASSIO_TOKEN}):
        yield HassIO(hass.loop, websession, "127.0.0.1")
