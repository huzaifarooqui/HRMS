from allocation_sync import sync_all
print("Starting one-time Allocation sync...")
sync_all()
print("One-time Allocation sync finished.")
print("Now refresh Employee > Allocation. If still empty, check Server\\allocation_sync.log.")
