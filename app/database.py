# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建 SQLite 数据库（文件存储）
SQLALCHEMY_DATABASE_URL = "sqlite:///./crypto_arbitrage.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

""" 这个是 SQLite 的特殊设置，默认情况下，SQLite 不允许多个线程同时访问同一个数据库文件。
这里设为 False，意思是 "允许多线程访问"，这样你的程序在并发运行时不会出错。
想象一下：
如果你只允许一个人进书店（数据库），其他人必须等前一个人出来，效率会很低。
这里的设置就是 "可以让多个店员同时进店工作"，不会因为“只能一个人操作”而卡住。 """

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)#制造打开这个database的工具
#SessionLocal 就是用来打开 Excel 的工具
#Example
# db = SessionLocal()  # 开启一个新的数据库会话（打开 Excel）
# db.add(new_data)      # 添加新数据（修改 Excel 表）
# db.commit()           # 保存更改（按下 Excel 的保存按钮）
# db.close()            # 关闭会话（关闭 Excel）


# ORM 基类
Base = declarative_base()
#class User(Base):  # 继承 Base，说明 User 是一个数据库表
#    __tablename__ = "users"
#    id = Column(Integer, primary_key=True)
#    name = Column(String)
# Dependency to get DB session



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()