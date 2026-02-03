import modal
app = modal.App("test-atomic")
@app.function()
def test():
    print("Atomic test success")
