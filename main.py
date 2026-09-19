from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, select

# --- MODELOS DE DATOS ---
class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str

class Factura(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    descripcion: str
    cliente_id: int = Field(foreign_key="cliente.id")

# --- CONFIGURACIÓN BASE DE DATOS LOCAL ---
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

# --- CRUD CLIENTES ---
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

@app.delete("/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    session.delete(cliente)
    session.commit()
    return {"mensaje": "Cliente eliminado"}

# --- CRUD FACTURAS ---
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