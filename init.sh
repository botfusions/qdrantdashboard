#!/bin/bash

# Initialize users.json if not exists
if [ ! -f "users.json" ]; then
    echo "Creating users.json from example..."
    cp users.json.example users.json
fi

# Initialize customers.json if not exists
if [ ! -f "customers.json" ]; then
    echo "Creating customers.json from example..."
    cp customers.json.example customers.json
fi

echo "Initialization complete!"
