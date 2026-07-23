from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

USERS = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$Hsdl3eAHDElAI0trH3p4getaiuvy6lJuzkhdpVhyxlzCSDGx1uP/.",
        "role": "admin",
    },
    "analyst": {
        "username": "analyst",
        "hashed_password": "$2b$12$DzjjXRq85Fp7xJvuoB5Br.UNntzi/lO0VXJCjCFPFhlNy.Wgq7eBa",
        "role": "analyst",
    },
}