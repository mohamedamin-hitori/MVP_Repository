import tkinter as tk
from tkinter import messagebox, ttk
from models import session, EntreeFIL, Fabrication, StockProduitFini, Sale
from utils import export_to_csv, generate_production_report

class FabricSection:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill='both', expand=True)

        # Form fields
        tk.Label(self.frame, text="Model:").grid(row=0, column=0)
        self.model_entry = tk.Entry(self.frame)
        self.model_entry.grid(row=0, column=1)

        tk.Label(self.frame, text="Price:").grid(row=1, column=0)
        self.price_entry = tk.Entry(self.frame)
        self.price_entry.grid(row=1, column=1)

        tk.Label(self.frame, text="Quantity:").grid(row=2, column=0)
        self.quantity_entry = tk.Entry(self.frame)
        self.quantity_entry.grid(row=2, column=1)

        tk.Label(self.frame, text="Supplier:").grid(row=3, column=0)
        self.supplier_entry = tk.Entry(self.frame)
        self.supplier_entry.grid(row=3, column=1)

        tk.Button(self.frame, text="Add Fabric", command=self.add_fabric).grid(row=4, column=0, columnspan=2)

        # Listbox to show fabric records
        self.fabric_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.fabric_listbox.grid(row=5, column=0, columnspan=2)

        # Add Export button
        tk.Button(self.frame, text="Export to CSV", command=self.export_fabrics_csv).grid(row=6, column=0, columnspan=2)

        self.load_fabrics()

    def add_fabric(self):
        model = self.model_entry.get()
        prix = float(self.price_entry.get())
        quantite = float(self.quantity_entry.get())
        fournisseur = self.supplier_entry.get()

        new_fabric = EntreeFIL(model_fil=model, prix=prix, quantite=quantite, fournisseur=fournisseur)
        session.add(new_fabric)
        session.commit()

        self.model_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.supplier_entry.delete(0, tk.END)

        self.load_fabrics()

    def load_fabrics(self):
        self.fabric_listbox.delete(0, tk.END)
        fabrics = session.query(EntreeFIL).all()
        for fabric in fabrics:
            self.fabric_listbox.insert(tk.END, f"{fabric.model_fil} - {fabric.quantite} kg - ${fabric.prix}")

    def export_fabrics_csv(self):
        fabrics = session.query(EntreeFIL).all()
        if fabrics:
            export_to_csv(fabrics, "fabrics.csv")
            messagebox.showinfo("Export Complete", "Fabrics exported to fabrics.csv")
        else:
            messagebox.showwarning("No Data", "No fabrics available to export.")


class ProductionSection:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill='both', expand=True)

        tk.Label(self.frame, text="Machine ID:").grid(row=0, column=0)
        self.machine_id_entry = tk.Entry(self.frame)
        self.machine_id_entry.grid(row=0, column=1)

        tk.Label(self.frame, text="Tissue ID:").grid(row=1, column=0)
        self.tissue_id_entry = tk.Entry(self.frame)
        self.tissue_id_entry.grid(row=1, column=1)

        tk.Label(self.frame, text="Quantity (kg):").grid(row=2, column=0)
        self.quantity_entry = tk.Entry(self.frame)
        self.quantity_entry.grid(row=2, column=1)

        tk.Button(self.frame, text="Add Production", command=self.add_production).grid(row=3, column=0, columnspan=2)

        # Listbox to show production records
        self.production_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.production_listbox.grid(row=4, column=0, columnspan=2)

        # Add Export button
        tk.Button(self.frame, text="Export to CSV", command=self.export_productions_csv).grid(row=5, column=0, columnspan=2)

        self.load_productions()

    def add_production(self):
        machine_id = int(self.machine_id_entry.get())
        tissue_id = int(self.tissue_id_entry.get())
        quantity = float(self.quantity_entry.get())

        new_production = Fabrication(id_machine=machine_id, id_tissue=tissue_id, quantite=quantity)
        session.add(new_production)

        # Update the stock based on production
        existing_stock = session.query(StockProduitFini).filter_by(id_tissue=tissue_id).first()
        if existing_stock:
            existing_stock.total_stock += quantity
        else:
            new_stock = StockProduitFini(
                id_tissue=tissue_id,
                total_stock=quantity,
                nom_produit=f"Tissue {tissue_id} Product",
                prix_unit=15.00  # Default price, adjust as needed
            )
            session.add(new_stock)

        session.commit()
        self.load_productions()

    def load_productions(self):
        self.production_listbox.delete(0, tk.END)
        productions = session.query(Fabrication).all()
        for production in productions:
            self.production_listbox.insert(tk.END, f"Machine: {production.id_machine}, Tissue: {production.id_tissue}, Quantity: {production.quantite} kg")

    def export_productions_csv(self):
        productions = session.query(Fabrication).all()
        if productions:
            export_to_csv(productions, "productions.csv")
            messagebox.showinfo("Export Complete", "Productions exported to productions.csv")
        else:
            messagebox.showwarning("No Data", "No productions available to export.")


class StockSection:
    def __init__(self, parent, notebook, tab_index):
        self.frame = tk.Frame(parent)
        self.notebook = notebook  # Reference to the notebook
        self.tab_index = tab_index  # The index of the Stock Management tab
        self.frame.pack(fill='both', expand=True)

        # Listbox to show stock records
        self.stock_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.stock_listbox.grid(row=0, column=0, columnspan=2)

        # Add Export button
        tk.Button(self.frame, text="Export to CSV", command=self.export_stock_csv).grid(row=1, column=0, columnspan=2)

        # Bind the event of switching tabs to refresh the stock list
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def load_stock(self):
        self.stock_listbox.delete(0, tk.END)
        stock_items = session.query(StockProduitFini).all()
        for item in stock_items:
            self.stock_listbox.insert(tk.END, f"Product: {item.nom_produit}, Quantity: {item.total_stock}, Price: ${item.prix_unit}")

    def export_stock_csv(self):
        stock_items = session.query(StockProduitFini).all()
        if stock_items:
            export_to_csv(stock_items, "stock.csv")
            messagebox.showinfo("Export Complete", "Stock data exported to stock.csv")
        else:
            messagebox.showwarning("No Data", "No stock data available to export.")

    def on_tab_change(self, event):
        # Get the index of the selected tab
        selected_tab = self.notebook.index(self.notebook.select())
        # Check if the selected tab is the "Stock Management" tab
        if selected_tab == self.tab_index:
            self.load_stock()

class SalesSection:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill='both', expand=True)

        tk.Label(self.frame, text="Stock ID:").grid(row=0, column=0)
        self.stock_id_entry = tk.Entry(self.frame)
        self.stock_id_entry.grid(row=0, column=1)

        tk.Label(self.frame, text="Quantity:").grid(row=1, column=0)
        self.quantity_entry = tk.Entry(self.frame)
        self.quantity_entry.grid(row=1, column=1)

        tk.Button(self.frame, text="Make Sale", command=self.make_sale).grid(row=2, column=0, columnspan=2)

        # Listbox to show sales history
        self.sales_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.sales_listbox.grid(row=3, column=0, columnspan=2)

        # Add Export button
        tk.Button(self.frame, text="Export to CSV", command=self.export_sales_csv).grid(row=4, column=0, columnspan=2)

        self.load_sales()

    def make_sale(self):
        stock_id = int(self.stock_id_entry.get())
        quantity = int(self.quantity_entry.get())

        stock_item = session.query(StockProduitFini).get(stock_id)
        if stock_item and stock_item.total_stock >= quantity:
            stock_item.total_stock -= quantity

            # Record the sale
            sale_record = Sale(
                stock_id=stock_id,
                product=stock_item.nom_produit,
                quantity=quantity,
                price=stock_item.prix_unit
            )
            session.add(sale_record)  # Add sale record to the Sale model
            session.commit()

            self.load_sales()
        else:
            messagebox.showerror("Error", "Not enough stock available")

    def load_sales(self):
        self.sales_listbox.delete(0, tk.END)
        sales = session.query(Sale).all()
        for sale in sales:
            self.sales_listbox.insert(tk.END, f"Product: {sale.product}, Quantity: {sale.quantity}, Price: ${sale.price}, Date: {sale.sale_date}")

    def export_sales_csv(self):
        sales = session.query(Sale).all()
        if sales:
            export_to_csv(sales, "sales.csv")
            messagebox.showinfo("Export Complete", "Sales history exported to sales.csv")
        else:
            messagebox.showwarning("No Data", "No sales history available to export.")




class ReportSection:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill='both', expand=True)

        tk.Button(self.frame, text="Generate Production Report", command=self.show_production_report).pack(pady=10)

    def show_production_report(self):
        report = generate_production_report()
        messagebox.showinfo("Production Report", report)


class ClothingFactoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clothing Factory Management System")

        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True)

        # Initialize each section
        self.fabric_section = FabricSection(notebook)
        notebook.add(self.fabric_section.frame, text="Fabric Management")

        self.production_section = ProductionSection(notebook)
        notebook.add(self.production_section.frame, text="Production")

        stock_tab_index = len(notebook.tabs())  # This will be the index of the Stock Management tab
        self.stock_section = StockSection(notebook, notebook, stock_tab_index)
        notebook.add(self.stock_section.frame, text="Stock Management")

        self.sales_section = SalesSection(notebook)
        notebook.add(self.sales_section.frame, text="Sales")

        self.report_section = ReportSection(notebook)
        notebook.add(self.report_section.frame, text="Reports")




if __name__ == '__main__':
    root = tk.Tk()
    app = ClothingFactoryApp(root)
    root.mainloop()
