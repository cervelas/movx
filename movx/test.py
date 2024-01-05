from h2o_wave import main, Q, app, ui

# Define some sample data to populate the tree view
data = {
    "Fruits": {
        "Apples": {
            "Red": ["Fuji", "Gala", "Cameo"],
            "Green": ["Granny Smith", "Golden Delicious"],
        },
        "Oranges": ["Navel", "Cara Cara", "Blood"],
        "Bananas": ["Cavendish", "Red"],
    },
    "Vegetables": {
        "Leafy Greens": ["Spinach", "Kale", "Collard Greens"],
        "Cruciferous Vegetables": ["Broccoli", "Cauliflower", "Brussels Sprouts"],
        "Root Vegetables": ["Carrots", "Potatoes", "Turnips"],
    },
}


# Define a function to recursively create the dropdown options
def create_dropdown_options(data, prefix=""):
    if isinstance(data, dict):
        options = []
        for key, value in data.items():
            children = create_dropdown_options(value, f"{prefix}{key} / ")
            option = ui.checklist(name=f"{prefix}{key}", label=key, choices=children)
            options.append(option)
        return options
    elif isinstance(data, list):
        options = [ui.label(name=f"{prefix}{name}", label=name) for name in data]
        return options


# Define the Wave app and layout
@app("/demo")
async def serve(q: Q):
    if not q.client.initialized:
        # Create the dropdown options and add the dropdown to the page
        options = create_dropdown_options(data)
        dropdown = ui.dropdown(
            name="treeview",
            label="Select a category / subcategory / item",
            value="",
            options=options,
        )
        q.client.initialized = True
        q.page["main"] = ui.form_card(box="1 1 12 10", items=[dropdown])
    else:
        # Handle changes to the dropdown value by updating the dropdown with the appropriate options
        value = q.args.treeview
        if value:
            options = create_dropdown_options(data, f"{value} / ")
            q.page["main"].items[0].options = options
    await q.page.save()


# Run the Wave app
if __name__ == "__main__":
    app()
