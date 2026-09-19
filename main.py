from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, select


class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str

class Factura(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    descripcion: str
    cliente_id: int = Field(foreign_key="cliente.id")


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="API Clientes y Facturas")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/clientes/", response_model=Cliente)
def crear_cliente(cliente: Cliente, session: Session = Depends(get_session)):
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return cliente

@app.get("/clientes/", response_model=List[Cliente])
def listar_clientes(session: Session = Depends(get_session)):
    return session.exec(select(Cliente)).all()

@app.get("/clientes/{cliente_id}", response_model=Cliente)
def obtener_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.put("/clientes/{cliente_id}", response_model=Cliente)
def actualizar_cliente(cliente_id: int, cliente_data: Cliente, session: Session = Depends(get_session)):
    cliente_db = session.get(Cliente, cliente_id)
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente_db.nombre = cliente_data.nombre
    cliente_db.email = cliente_data.email
    
    session.add(cliente_db)
    session.commit()
    session.refresh(cliente_db)
    return cliente_db

@app.delete("/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    session.delete(cliente)
    session.commit()
    return {"mensaje": "Cliente eliminado"}


@app.post("/facturas/", response_model=Factura)
def crear_factura(factura: Factura, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, factura.cliente_id)
    if not cliente:
        raise HTTPException(status_code=400, detail="El cliente especificado no existe")
    session.add(factura)
    session.commit()
    session.refresh(factura)
    return factura

@app.get("/facturas/", response_model=List[Factura])
def listar_facturas(session: Session = Depends(get_session)):
    return session.exec(select(Factura)).all()

@app.get("/facturas/{factura_id}", response_model=Factura)
def obtener_factura(factura_id: int, session: Session = Depends(get_session)):
    factura = session.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura


@app.put("/facturas/{factura_id}", response_model=Factura)
def actualizar_factura(factura_id: int, factura_data: Factura, session: Session = Depends(get_session)):
    factura_db = session.get(Factura, factura_id)
    if not factura_db:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    

    cliente = session.get(Cliente, factura_data.cliente_id)
    if not cliente:
        raise HTTPException(status_code=400, detail="El cliente especificado no existe")

    factura_db.monto = factura_data.monto
    factura_db.descripcion = factura_data.descripcion
    factura_db.cliente_id = factura_data.cliente_id

    session.add(factura_db)
    session.commit()
    session.refresh(factura_db)
    return factura_db


@app.delete("/facturas/{factura_id}")
def eliminar_factura(factura_id: int, session: Session = Depends(get_session)):
    factura = session.get(Factura, factura_id)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    session.delete(factura)
    session.commit()
    return {"mensaje": "Factura eliminada"}