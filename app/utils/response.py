def ok(data=None, message="ok"):
    return {"message": message, "data": data}

def err(message="error"):
    return {"message": message}
