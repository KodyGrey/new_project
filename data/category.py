import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Category(SqlAlchemyBase):
    __tablename__ = 'category'

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String)


association_table = sqlalchemy.Table(
    'jobs_to_category',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('jobs', sqlalchemy.Integer, sqlalchemy.ForeignKey('jobs.id')),
    sqlalchemy.Column('category', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('category.id'))
)
