import tkinter as tk
from src.core.app import CommandCenter
from src.ui.main_window import CommandCenterUI

def main():
    # Initialize command center
    command_center = CommandCenter()

    try:
        command_center.initialize_features()
        command_center.start_background_services()

        # Start UI
        root = tk.Tk()
        app = CommandCenterUI(root, command_center)

        print("Personal Command Center started")
        print("Press Ctrl+Space to open the search interface")

        # Keep the application running
        root.mainloop()

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        command_center.stop_background_services()
    
if __name__ == "__main__":
    main()