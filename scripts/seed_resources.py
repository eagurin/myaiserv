import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.app.db.session import async_session
from src.app.models.resource import Resource


async def seed_resources(session: AsyncSession) -> None:
    """Заполнение базы данных начальными ресурсами"""

    initial_resources = [
        {
            "name": "crypto",
            "type": "primary",
            "description": "Криптовалюта - основной ресурс",
            "initial_amount": 10000,
            "max_amount": 1000000,
            "generation_rate": 1.0,
            "is_active": True,
        },
        {
            "name": "energy",
            "type": "primary",
            "description": "Энергия для майнинга",
            "initial_amount": 5000,
            "max_amount": 500000,
            "generation_rate": 0.8,
            "is_active": True,
        },
        {
            "name": "computing_power",
            "type": "secondary",
            "description": "Вычислительная мощность",
            "initial_amount": 1000,
            "max_amount": 100000,
            "generation_rate": 0.5,
            "is_active": True,
        },
    ]

    for resource_data in initial_resources:
        resource = Resource(
            name=resource_data["name"],
            type=resource_data["type"],
            description=resource_data["description"],
            initial_amount=resource_data["initial_amount"],
            current_amount=resource_data["initial_amount"],
            max_amount=resource_data["max_amount"],
            generation_rate=resource_data["generation_rate"],
            is_active=resource_data["is_active"],
            last_updated=datetime.utcnow(),
        )
        session.add(resource)

    await session.commit()


async def main() -> None:
    """Точка входа для заполнения базы данных"""
    async with async_session() as session:
        await seed_resources(session)
        print("База данных успешно заполнена тестовыми ресурсами")


if __name__ == "__main__":
    asyncio.run(main())
