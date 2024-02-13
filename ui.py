import tkinter as tk

def create_ui():
    root = tk.Tk()
    root.title("PID Controller UI")

    label1 = tk.Label(root, text="Number of Threads:")
    label1.pack()
    entry1 = tk.Entry(root)
    entry1.pack()

    label2 = tk.Label(root, text="Number of Iterations:")
    label2.pack()
    entry2 = tk.Entry(root)
    entry2.pack()

    button = tk.Button(root, text="Start Simulation", command=lambda: start_simulation(entry1.get(), entry2.get()))
    button.pack()

    root.mainloop()

def start_simulation(num_threads, num_iterations):
    # Add your simulation logic here
    print(f"Starting simulation with {num_threads} threads and {num_iterations} iterations")

if __name__ == '__main__':
    create_ui()