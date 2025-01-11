import torch

print(torch.cuda.device_count())
print(torch.version.cuda)
print(torch.cuda.is_available())

torch.cuda.empty_cache()   # Releases cached memory back to the system
torch.cuda.reset_max_memory_allocated()  # Resets memory statistics

x = torch.rand((1024, 1024), device='cuda')
print(x)