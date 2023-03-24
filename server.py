from flask import Flask, request, jsonify
from flask.views import MethodView
import atexit
from sqlalchemy import Column, String, Integer, DateTime, create_engine, func, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, ValidationError
from typing import Optional


class HttpError(Exception):

    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


class CreateUser(BaseModel):

    username: str
    password: str


class CreateAdv(BaseModel):

    title: str
    description: str
    user_id: int


class PatchAdv(BaseModel):

    title: Optional[str]
    description: Optional[str]


def validate_create_user(json_data):

    try:
        user_schema = CreateUser(**json_data)
        return user_schema.dict()
    except ValidationError as er:
        raise HttpError(status_code=400, message=er.errors())


def validate_adv(schema, data):
    try:
        return schema(**data).dict()
    except ValidationError as error:
        raise HttpError(400, error.errors())


app = Flask('server')


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    http_response = jsonify({'status': 'error', 'description': error.message})
    http_response.status_code = error.status_code
    return http_response


PG_DSN = 'postgresql://postgres:TPD37486IQ@127.0.0.1:5431/testdb'
engine = create_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)
atexit.register(engine.dispose)


class User(Base):

    __tablename__ = 'ads_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    registration_time = Column(DateTime, server_default=func.now())


def get_user(session: Session, user_id: int):
    user = session.query(User).get(user_id)
    if user is None:
        raise HttpError(404, 'user not found')
    return user


class Adv(Base):

    __tablename__ = "advertisement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("ads_users.id", ondelete="CASCADE"))
    user = relationship("User", lazy="joined")


def get_adv(session: Session, adv_id: int):
    adv = session.query(Adv).get(adv_id)
    if adv is None:
        raise HttpError(404, 'advertisement not found')
    return adv


Base.metadata.create_all(bind=engine)


class UserView(MethodView):

    def get(self, user_id: int):

        with Session() as session:
            user = get_user(session, user_id)
            return jsonify(
                {"id": user.id, 'user': user.username, "registration_time": user.registration_time.isoformat()})

    def post(self):

        json_data = request.json
        with Session() as session:
            new_user = User(**json_data)
            session.add(new_user)
            session.commit()
            return jsonify(
                {
                    'id': new_user.id,
                    'name': new_user.username
                }
            )


class AdvView(MethodView):

    def get(self, adv_id: int):

        with Session() as session:
            adv = get_adv(session, adv_id)
            return jsonify({
                'id': adv_id,
                'title': adv.title,
                'user': adv.user_id,
            })

    def post(self):

        json_data = request.json
        validated_data = validate_adv(CreateAdv, json_data)
        with Session() as session:
            user = session.query(User).filter(User.id == validated_data['user_id']).first()
            if user is None:
                raise HttpError(401, "Invalid user")

            new_adv = Adv(user=user, title=validated_data['title'], description=validated_data['description'])
            session.add(new_adv)
            session.commit()
            return jsonify(
                {
                    'id': new_adv.id,
                    'title': new_adv.title
                }
            )

    def patch(self, adv_id: int):

        json_data = request.json
        validated_data = validate_adv(PatchAdv, json_data)
        with Session() as session:
            adv = get_adv(session, adv_id)
            if validated_data.get('title'):
                adv.title = validated_data['title']
            if validated_data.get('description'):
                adv.description = validated_data['description']
            session.add(adv)
            session.commit()
            return jsonify({'status': 'success'})

    def delete(self, adv_id: int):
        with Session() as session:
            adv = get_adv(session, adv_id)
            session.delete(adv)
            session.commit()
            return jsonify({'status': 'success'})


app.add_url_rule('/users/<int:user_id>', view_func=UserView.as_view('users_with_id'),
                 methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/users', view_func=UserView.as_view('users'), methods=['POST'])

app.add_url_rule('/adv/<int:adv_id>', view_func=AdvView.as_view('adv_with_id'),
                 methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/adv', view_func=AdvView.as_view('advertisements'), methods=['POST'])

app.run(port=5000)
