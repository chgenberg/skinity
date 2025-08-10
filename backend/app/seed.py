from sqlmodel import Session, select
from .database import engine, create_db_and_tables
from .models import Provider, Product


def seed() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        count = session.exec(select(Provider)).first()
        if count:
            return
        provider = Provider(
            name="ExampleBrand",
            website="https://example.com",
            country="SE",
            description="Exempelvarumärke för att verifiera flödet",
            pros=["Prisvärd", "Skonsam"],
            cons=["Begränsat produktutbud"],
            tags=["vegan", "cruelty-free"],
        )
        session.add(provider)
        session.commit()
        session.refresh(provider)

        products = [
            Product(
                provider_id=provider.id,
                name="Hydrating Serum",
                url="https://example.com/serum",
                description="Återfuktande serum med hyaluronsyra",
                price_amount=249.0,
                price_currency="SEK",
                tags=["serum", "hydrating"],
                skin_types=["normal", "torr"],
                rating=4.5,
            ),
            Product(
                provider_id=provider.id,
                name="Gentle Cleanser",
                url="https://example.com/cleanser",
                description="Mild rengöring för dagligt bruk",
                price_amount=149.0,
                price_currency="SEK",
                tags=["cleanser", "gentle"],
                skin_types=["känslig", "normal"],
                rating=4.2,
            ),
        ]
        for p in products:
            session.add(p)
        session.commit()


if __name__ == "__main__":
    seed() 