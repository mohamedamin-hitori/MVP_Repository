from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class EntreeFIL(Base):
    __tablename__ = 'entree_fil'
    id_fil = Column(Integer, primary_key=True)
    dt_entree = Column(DateTime, default=datetime.utcnow)
    prix = Column(Float)
    model_fil = Column(String(100))
    quantite = Column(Float)
    fournisseur = Column(String(100))
    description = Column(String(200))

class Machine(Base):
    __tablename__ = 'machine'
    id_machine = Column(Integer, primary_key=True)
    nom_machine = Column(String(100))
    emplacement = Column(String(100))
    type_machine = Column(String(100))

class Tissue(Base):
    __tablename__ = 'tissue'
    id_tissue = Column(Integer, primary_key=True)
    model_tissue = Column(String(100))
    nb_roulau = Column(Integer)
    quantite = Column(Float)
    id_fil = Column(Integer, ForeignKey('entree_fil.id_fil'))
    id_machine = Column(Integer, ForeignKey('machine.id_machine'))
    description = Column(String(200))

class Fabrication(Base):
    __tablename__ = 'fabrication'
    id_fabrication = Column(Integer, primary_key=True)
    dt_fabrication = Column(DateTime, default=datetime.utcnow)
    id_machine = Column(Integer, ForeignKey('machine.id_machine'))
    id_tissue = Column(Integer, ForeignKey('tissue.id_tissue'))
    id_fil = Column(Integer, ForeignKey('entree_fil.id_fil'))
    type_fil = Column(String(100))
    nb_fabrication = Column(Integer)
    nb_h_fabrication = Column(Float)
    quantite = Column(Float)
    pourcentage_chute = Column(Float)

class StockProduitFini(Base):
    __tablename__ = 'stock_produit_fini'
    id_stock = Column(Integer, primary_key=True)
    id_tissue = Column(Integer, ForeignKey('tissue.id_tissue'))
    dt_stock = Column(DateTime, default=datetime.utcnow)
    total_stock = Column(Float)
    nom_produit = Column(String(100))
    prix_unit = Column(Float)

    sales = relationship("Sale", back_populates="stock")

class Sale(Base):
    __tablename__ = 'sales'
    id_sale = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stock_produit_fini.id_stock'))
    product = Column(String(100))
    quantity = Column(Integer)
    price = Column(Float)
    sale_date = Column(DateTime, default=datetime.utcnow)

    stock = relationship("StockProduitFini", back_populates="sales")

class Client(Base):
    __tablename__ = 'client'
    matricule = Column(Integer, primary_key=True)
    nom = Column(String(100))
    prenom = Column(String(100))

# Database setup
engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
