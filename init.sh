#!/bin/bash

# Always recreate users.json from example to ensure correct format
echo "Creating users.json from example..."
cp users.json.example users.json

# Initialize customers.json if not exists
if [ ! -f "customers.json" ]; then
    echo "Creating customers.json from example..."
    cp customers.json.example customers.json
fi

echo "Initialization complete!"
