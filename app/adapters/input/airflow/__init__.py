"""Airflow input adapter."""

from template.app.adapters.input.airflow.operators import ConsumerOperator, ProducerOperator

__all__ = ["ConsumerOperator", "ProducerOperator"]
