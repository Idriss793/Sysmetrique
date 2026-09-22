import subprocess
from unittest.mock import Mock, patch

import pytest

from app.collector import (
    MetricsCollectionError,
    collect_system_metrics,
    get_load_average,
)


@patch("app.collector.subprocess.run")
def test_get_load_average_success(mock_run):
    """Vérifie la récupération correcte des métriques de charge."""
    mock_run.return_value = Mock(
        stdout=" 10:00:00 up 2 days, load average: 0.10, 0.20, 0.30\n"
    )

    result = get_load_average()

    assert result == {
        "load_1m": 0.10,
        "load_5m": 0.20,
        "load_15m": 0.30,
    }
    # S'assure que subprocess a bien été appelé avec les bons arguments
    mock_run.assert_called_once()


@pytest.mark.parametrize(
    "stdout_output,expected",
    [
        (
            " 12:34:56 up 1 day,  1:23,  load average: 1.50, 2.00, 2.50\n",
            {"load_1m": 1.50, "load_5m": 2.00, "load_15m": 2.50},
        ),
        (
            " 00:00:01 up 5 mins, load average: 0.00, 0.01, 0.05\n",
            {"load_1m": 0.0, "load_5m": 0.01, "load_15m": 0.05},
        ),
    ],
)
@patch("app.collector.subprocess.run")
def test_get_load_average_various_formats(mock_run, stdout_output, expected):
    """Vérifie que différents formats de sortie de la commande sont bien parsés."""
    mock_run.return_value = Mock(stdout=stdout_output)
    assert get_load_average() == expected


@patch("app.collector.subprocess.run")
def test_get_load_average_subprocess_error(mock_run):
    """Vérifie qu'une erreur de subprocess lève bien l'exception métier."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "uptime")

    with pytest.raises(MetricsCollectionError):
        get_load_average()


@patch("app.collector.subprocess.run")
def test_get_load_average_invalid_format(mock_run):
    """Vérifie qu'un format de sortie inattendu lève l'exception métier."""
    mock_run.return_value = Mock(stdout="invalid format output\n")

    with pytest.raises(MetricsCollectionError):
        get_load_average()