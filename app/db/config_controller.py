def get_sysvalue(name:str):
    from app.db.models import SysValues
    from app.db.session import get_session
    from sqlmodel import select

    with get_session() as session:
        value = session.exec(select(SysValues).where(SysValues.name == name)).first()
        if(value == None): return None
        return value.value


def get_sysvalue_all():
    from app.db.models import SysValues
    from app.db.session import get_session
    from sqlmodel import select

    with get_session() as session:
        return session.exec(select(SysValues)).all()
    
def set_sysvalue(name:str, value:str):
    from app.db.models import SysValues
    from app.db.session import get_session
    from sqlmodel import select, insert, update

    with get_session() as session:
        entry = session.exec(select(SysValues).where(SysValues.name == name)).first()

        if(entry == None):
            session.exec(insert(SysValues).values(name=name,value=value))
        else:
            session.exec(update(SysValues).where(SysValues.name == name).values(value=value))
        
        session.commit()

        