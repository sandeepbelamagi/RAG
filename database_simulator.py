class DatabaseSimulator:
    """
    A simple in-memory simulator for basic database CRUD operations.
    Uses a dictionary to store records, keyed by an auto-incrementing ID.
    """
    def __init__(self):
        # Simulate storage: {id: record_data}
        self.records = {}
        self.next_id = 1
        print("DatabaseSimulator initialized. Ready for operations.")

    def create_record(self, record: dict) -> int:
        """
        Creates a new record and returns its assigned ID.

        Args:
            record: A dictionary containing the data for the new record.

        Returns:
            The unique ID assigned to the new record.
        """
        if not record or not isinstance(record, dict):
            raise ValueError("Record must be a non-empty dictionary.")

        record_id = self.next_id
        self.records[record_id] = record.copy()
        self.next_id += 1
        print(f"\n[SUCCESS] Created record with ID {record_id}: {record}")
        return record_id

    def read_record(self, record_id: int) -> dict or None:
        """
        Reads a record by its ID.

        Args:
            record_id: The unique ID of the record to retrieve.

        Returns:
            A dictionary containing the record data, or None if not found.
        """
        if record_id <= 0:
            raise ValueError("Record ID must be a positive integer.")

        record = self.records.get(record_id)
        if record:
            print(f"\n[SUCCESS] Read record ID {record_id}: {record}")
        else:
            print(f"\n[FAIL] No record found with ID {record_id}.")
        return record

    def update_record(self, record_id: int, updates: dict) -> bool:
        """
        Updates fields for an existing record by ID.

        Args:
            record_id: The unique ID of the record to update.
            updates: A dictionary containing the fields and new values.

        Returns:
            True if the update was successful, False otherwise.
        """
        if record_id not in self.records:
            print(f"\n[FAIL] Cannot update. No record found with ID {record_id}.")
            return False

        if not updates or not isinstance(updates, dict):
            print("\n[WARN] No updates provided.")
            return False

        # Apply updates, ensuring we don't overwrite the entire record just because we updated one field
        self.records[record_id].update(updates)
        print(f"\n[SUCCESS] Updated record ID {record_id} with new data: {updates}")
        return True

    def delete_record(self, record_id: int) -> bool:
        """
        Deletes a record by its ID.

        Args:
            record_id: The unique ID of the record to delete.

        Returns:
            True if the record was deleted, False if it did not exist.
        """
        if record_id not in self.records:
            print(f"\n[FAIL] Cannot delete. No record found with ID {record_id}.")
            return False

        del self.records[record_id]
        print(f"\n[SUCCESS] Deleted record with ID {record_id}.")
        return True

# --- Example Usage ---
if __name__ == "__main__":
    # 1. Initialize the simulator
    db = DatabaseSimulator()

    # 2. CREATE Operation (C)
    print("-" * 30)
    # Create user A
    user_a = {"username": "alice", "email": "alice@example.com", "status": "active"}
    id_alice = db.create_record(user_a)

    # Create user B
    user_b = {"username": "bob", "email": "bob@example.com", "status": "inactive"}
    id_bob = db.create_record(user_b)
    print("-" * 30)

    # 3. READ Operation (R)
    print("--- Testing Read (R) ---")
    # Read existing user
    db.read_record(id_alice)
    # Read non-existent user
    db.read_record(999)
    print("-" * 30)

    # 4. UPDATE Operation (U)
    print("--- Testing Update (U) ---")
    # Update Alice's status
    updates_alice = {"status": "pending", "last_login": "2024-01-01"}
    db.update_record(id_alice, updates_alice)

    # Attempt to update a non-existent user
    db.update_record(999, {"status": "online"})
    print("-" * 30)

    # 5. DELETE Operation (D)
    print("--- Testing Delete (D) ---")
    # Delete Bob
    db.delete_record(id_bob)

    # Attempt to delete the same user again
    db.delete_record(id_bob)
    print("-" * 30)

    # Final check on the updated record
    print("--- Final Read Check ---")
    db.read_record(id_alice)

    # Optional: Display all remaining records
    print("\n===== FINAL DATABASE STATE =====")
    print(f"Total records remaining: {len(db.records)}")
    print(db.records)