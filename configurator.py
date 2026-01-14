import customtkinter as ctk
import json5 as json_lib
import os
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import sys
import random
import colorsys

# Set default appearance mode and color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"

ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PicklistManager:
    def __init__(self, filepath="picklists.json"):
        self.filepath = filepath
        self.regions = []
        self.accounts = []
        self.load_picklists()

    def load_picklists(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json_lib.load(f)
                    self.regions = data.get("regions", [])
                    self.accounts = data.get("accounts", [])
            except Exception as e:
                print(f"Error loading picklists: {e}")
                self.regions = []
                self.accounts = []
        else:
            self.regions = []
            self.accounts = []

    def save_picklists(self):
        data = {
            "regions": self.regions,
            "accounts": self.accounts
        }
        try:
            with open(self.filepath, 'w') as f:
                json_lib.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving picklists: {e}")

    def add_region(self, region):
        if region and region not in self.regions:
            self.regions.append(region)
            self.regions.sort()
            self.save_picklists()
            return True
        return False

    def remove_region(self, region):
        if region in self.regions:
            self.regions.remove(region)
            self.save_picklists()
            return True
        return False

    def add_account(self, account_id, name):
        if not account_id: return False
        # Check if ID exists
        for acc in self.accounts:
            if acc["id"] == account_id:
                return False
        self.accounts.append({"id": account_id, "name": name})
        # Sort by name?
        self.accounts.sort(key=lambda x: x["name"])
        self.save_picklists()
        return True

    def remove_account(self, account_id):
        initial_len = len(self.accounts)
        self.accounts = [acc for acc in self.accounts if acc["id"] != account_id]
        if len(self.accounts) < initial_len:
            self.save_picklists()
            return True
        return False

    def get_account_display_list(self):
        return [f"{acc['name']} ({acc['id']})" for acc in self.accounts]
        
    def get_account_id_from_display(self, display_str):
        if not display_str: return ""
        if "(" in display_str and display_str.endswith(")"):
            return display_str.split("(")[-1].strip(")")
        return display_str

    def get_account_name(self, account_id):
        if not account_id: return ""
        for acc in self.accounts:
            if acc["id"] == account_id:
                return acc["name"]
        return ""

class PicklistEditor(ctk.CTkToplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.title("Manage Picklists")
        self.title("Manage Picklists")
        
        # Position relative to parent
        try:
            px = parent.winfo_x()
            py = parent.winfo_y()
            # Offset slightly
            self.geometry(f"600x500+{px+50}+{py+50}")
        except:
             self.geometry("600x500")
        
        # Stay on top of parent
        self.transient(parent)
        self.lift()
        self.focus_force()
        self.after(200, lambda: self.focus()) # Ensure focus sticks

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_regions = self.tabview.add("Regions")
        self.tab_accounts = self.tabview.add("Accounts")
        
        self.setup_regions_tab()
        self.setup_accounts_tab()
        
    def setup_regions_tab(self):
        # Add Area
        add_frame = ctk.CTkFrame(self.tab_regions)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        self.region_entry = ctk.CTkEntry(add_frame, placeholder_text="Region Code (e.g. us-west-2)")
        self.region_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        add_btn = ctk.CTkButton(add_frame, text="Add", width=80, command=self.add_region)
        add_btn.pack(side="left", padx=5)
        
        # List Area
        self.regions_scroll = ctk.CTkScrollableFrame(self.tab_regions, label_text="Existing Regions")
        self.regions_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_regions()
        
    def refresh_regions(self):
        for widget in self.regions_scroll.winfo_children():
            widget.destroy()
            
        for region in self.manager.regions:
            row = ctk.CTkFrame(self.regions_scroll)
            row.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(row, text=region).pack(side="left", padx=5)
            ctk.CTkButton(row, text="X", width=30, fg_color="red", command=lambda r=region: self.delete_region(r)).pack(side="right", padx=5)

    def add_region(self):
        val = self.region_entry.get().strip()
        if self.manager.add_region(val):
            self.region_entry.delete(0, "end")
            self.refresh_regions()
            
    def delete_region(self, region):
        if self.manager.remove_region(region):
            self.refresh_regions()

    def setup_accounts_tab(self):
        # Add Area
        add_frame = ctk.CTkFrame(self.tab_accounts)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        self.acc_id_entry = ctk.CTkEntry(add_frame, placeholder_text="Account ID")
        self.acc_id_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        self.acc_name_entry = ctk.CTkEntry(add_frame, placeholder_text="Account Name")
        self.acc_name_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        add_btn = ctk.CTkButton(add_frame, text="Add", width=80, command=self.add_account)
        add_btn.pack(side="left", padx=5)
        
        # List Area
        self.accounts_scroll = ctk.CTkScrollableFrame(self.tab_accounts, label_text="Existing Accounts")
        self.accounts_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_accounts()

    def refresh_accounts(self):
        for widget in self.accounts_scroll.winfo_children():
            widget.destroy()
            
        for acc in self.manager.accounts:
            row = ctk.CTkFrame(self.accounts_scroll)
            row.pack(fill="x", padx=5, pady=2)
            label = f"{acc['name']} ({acc['id']})"
            ctk.CTkLabel(row, text=label).pack(side="left", padx=5)
            ctk.CTkButton(row, text="X", width=30, fg_color="red", command=lambda id=acc['id']: self.delete_account(id)).pack(side="right", padx=5)

    def add_account(self):
        aid = self.acc_id_entry.get().strip()
        name = self.acc_name_entry.get().strip()
        if aid and name:
            if self.manager.add_account(aid, name):
                self.acc_id_entry.delete(0, "end")
                self.acc_name_entry.delete(0, "end")
                self.refresh_accounts()
            else:
                messagebox.showerror("Error", "Account ID already exists or invalid.")
    
    def delete_account(self, aid):
        if self.manager.remove_account(aid):
            self.refresh_accounts()

class ConfiguratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Configuration Tool")
        self.title("Configuration Tool")
        
        self.window_config_file = "window_config.json"
        self.apply_window_settings()
        
        # Bind close event to save window state
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.picklist_manager = PicklistManager()
        self.picklist_window = None
        self.filepath = None
        self.config_data = []

        # Setup GUI Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header Frame
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="AWS Peacock Configurator", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left", padx=10, pady=10)

        self.save_button = ctk.CTkButton(self.header_frame, text="Save Config", command=self.save_config, state="disabled")
        self.save_button.pack(side="right", padx=10)
        
        self.load_button = ctk.CTkButton(self.header_frame, text="Load Config", command=self.load_config_dialog)
        self.load_button.pack(side="right", padx=10)

        self.copy_button = ctk.CTkButton(self.header_frame, text="Copy Config", command=self.copy_to_clipboard, fg_color="gray", hover_color="gray30")
        self.copy_button.pack(side="right", padx=10)

        self.manage_picklists_btn = ctk.CTkButton(self.header_frame, text="Manage Picklists", command=self.open_picklist_manager)
        self.manage_picklists_btn.pack(side="right", padx=10)

        self.add_block_btn = ctk.CTkButton(self.header_frame, text="+ Add Block", command=self.add_config_block, fg_color="green", hover_color="darkgreen")
        self.add_block_btn.pack(side="right", padx=10)

        # Controls Frame (Expand/Collapse + Title)
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="ew")
        
        # Title "Configuration Items"
        self.config_items_label = ctk.CTkLabel(self.controls_frame, text="Configuration Items", font=ctk.CTkFont(size=16, weight="bold"))
        self.config_items_label.pack(side="left", padx=5)

        # Buttons (Right aligned)
        self.collapse_all_btn = ctk.CTkButton(self.controls_frame, text="Collapse All", height=24, width=80, command=self.collapse_all)
        self.collapse_all_btn.pack(side="right", padx=5)
        
        self.expand_all_btn = ctk.CTkButton(self.controls_frame, text="Expand All", height=24, width=80, command=self.expand_all)
        self.expand_all_btn.pack(side="right", padx=5)
        
        # Scrollable area for config items
        self.scrollable_frame = ctk.CTkScrollableFrame(self) # Removed label_text
        self.scrollable_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Try to load default file if exists
        default_file = os.path.join(os.getcwd(), "examples", "CoSD_SSO_Configuration.json")
        if os.path.exists(default_file):
            self.load_config(default_file)

    def open_picklist_manager(self):
        if self.picklist_window is None or not self.picklist_window.winfo_exists():
            self.picklist_window = PicklistEditor(self, self.picklist_manager)
            # Handle closing to clean up reference (optional but good practice)
            # self.picklist_window.protocol("WM_DELETE_WINDOW", self.on_picklist_close)
        else:
            self.picklist_window.lift()
            self.picklist_window.focus()


    def load_config_dialog(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if filename:
            self.load_config(filename)

    def load_config(self, filepath):
        try:
            with open(filepath, 'r') as f:
                self.config_data = json_lib.load(f)
            
            self.filepath = filepath
            self.title(f"Configuration Tool - {os.path.basename(filepath)}")
            self.save_button.configure(state="normal")
            self.render_config_items()
            print(f"Loaded {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def add_config_block(self):
        # Sync current state before adding/re-rendering to preserve edits
        self.sync_widgets_to_data()
        
        new_block = {
            "env": {
                "account": "",
                "region": ""
            },
            "style": {
                "navigationBackgroundColor": "#ffffff",
                "accountMenuButtonBackgroundColor": "#ffffff"
            }
        }
        self.config_data.append(new_block)
        self.render_config_items()
        
        # Scroll to bottom (optional, but good UX)
        self.scrollable_frame._parent_canvas.yview_moveto(1.0)

    def expand_all(self):
        self.sync_widgets_to_data()
        for item in self.config_data:
            item["_collapsed"] = False
        self.render_config_items()

    def collapse_all(self):
        self.sync_widgets_to_data()
        for item in self.config_data:
            item["_collapsed"] = True
        self.render_config_items()

    def render_config_items(self):
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.config_data):
            self.create_config_card(idx, item)

    def create_config_card(self, index, item):
        # Reset widget tracking for this render to avoid stale references
        item["_style_widgets"] = []
        
        card = ctk.CTkFrame(self.scrollable_frame)
        card.grid(row=index, column=0, padx=10, pady=10, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        # Label/Header for the card
        # Logic to construct header text: Name (ID) - Region
        header_text = f"Block #{index + 1}"
        
        envs = item.get("env", [])
        if isinstance(envs, dict):
            envs = [envs]
            
        # Collect unique info for summary
        summary_parts = []
        if envs:
            for env in envs:
                acc_id = env.get("account", "")
                region = env.get("region", "")
                acc_name = self.picklist_manager.get_account_name(acc_id)
                
                part = ""
                if acc_name:
                    part = f"{acc_name} ({acc_id})"
                elif acc_id:
                    part = f"{acc_id}"
                
                if region:
                    if part:
                         part += f" - {region}"
                    else:
                         part = region
                
                if part:
                    summary_parts.append(part)
        
        if summary_parts:
            # Join with newlines for multiple environments
            header_text = "\n".join(summary_parts)
        else:
            header_text = "Empty Configuration"

        # Styled Header
        header_frame = ctk.CTkFrame(card, fg_color=("gray85", "gray25"), corner_radius=6)
        header_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Collapse/Expand Toggle
        is_collapsed = item.get("_collapsed", False)
        toggle_char = "▶" if is_collapsed else "▼"
        
        def toggle_collapse():
            item["_collapsed"] = not item.get("_collapsed", False)
            # To update efficiently, we could just pack_forget/pack
            # But we need refs. Let's just re-render for simplicity and robustness first, 
            # or try to toggle visibility if referenced.
            # Re-rendering is safest for layout but heavier.
            # Let's try direct widget manipulation for speed.
            if item["_collapsed"]:
                toggle_btn.configure(text="▶")
                content_frame.grid_remove() # Hide
            else:
                toggle_btn.configure(text="▼")
                content_frame.grid() # Show
        
        toggle_btn = ctk.CTkButton(header_frame, text=toggle_char, width=30, fg_color="transparent", text_color=("black", "white"), hover_color=("gray75", "gray35"), command=toggle_collapse)
        toggle_btn.pack(side="left", padx=(5,0))

        card_label = ctk.CTkLabel(header_frame, text=header_text, font=ctk.CTkFont(size=14, weight="bold"))
        card_label.pack(side="left", padx=10, pady=5)
        
        # Add Delete Block Button
        def delete_block(idx=index):
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this block?"):
                self.sync_widgets_to_data()
                del self.config_data[idx]
                self.render_config_items()

        del_btn = ctk.CTkButton(header_frame, text="Delete Block", width=80, fg_color="darkred", hover_color="#800000", command=delete_block)
        del_btn.pack(side="right", padx=10, pady=5)

        # Content Frame (Collapsible)
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        if is_collapsed:
            content_frame.grid_remove()
        
        # Environment Section
        env_frame = ctk.CTkFrame(content_frame)
        env_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(env_frame, text="Environments", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=2)
        
        self.create_env_rows(env_frame, item)

        add_env_btn = ctk.CTkButton(env_frame, text="+ Add Environment", width=120, command=lambda: self.add_single_env_row(item["_env_container"], {}))
        add_env_btn.pack(anchor="w", padx=5, pady=5)


        # Style Section
        style_frame = ctk.CTkFrame(content_frame)
        style_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(style_frame, text="Styles", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=2)

        styles = item.get("style", {})
        
        # Generator Button
        def generate_theme():
            primary, secondary = self.generate_harmonious_colors()
            
            # Find widgets and update
            # We stored them in item["_style_widgets"] as (key, entry)
            # We need to find specific keys
            
            updates = {
                "navigationBackgroundColor": primary,
                "accountMenuButtonBackgroundColor": secondary
            }
            
            # Helper to find entry by key
            if "_style_widgets" in item:
                for key, entry in item["_style_widgets"]:
                    if key in updates:
                        # Update Entry
                        entry.delete(0, "end")
                        entry.insert(0, updates[key])
                        # Update internal dict
                        styles[key] = updates[key]

        # Improved approach: Update data model then re-render
        def generate_theme_action():
            primary, secondary = self.generate_harmonious_colors()
            styles["navigationBackgroundColor"] = primary
            styles["accountMenuButtonBackgroundColor"] = secondary
            self.render_config_items()

        gen_btn = ctk.CTkButton(style_frame, text="Generate Theme", fg_color="purple", hover_color="purple", command=generate_theme_action)
        gen_btn.pack(anchor="w", padx=5, pady=5)
        
        # Navigation Background Color
        self.create_color_row(style_frame, styles, "navigationBackgroundColor", "Nav Bg Color", item)
        # Account Menu Button Background Color
        self.create_color_row(style_frame, styles, "accountMenuButtonBackgroundColor", "Menu Button Bg", item)

    def create_color_row(self, parent, style_dict, key, label_text, item_ref):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(row, text=label_text, width=150, anchor="w").pack(side="left")
        
        current_color = style_dict.get(key, "#ffffff")
        
        # Color Preview/Button
        color_btn = ctk.CTkButton(row, text="", width=30, height=30, fg_color=current_color, border_width=2, border_color="gray")
        color_btn.pack(side="left", padx=5)
        
        # Entry
        entry = ctk.CTkEntry(row, width=100)
        entry.insert(0, current_color)
        entry.pack(side="left", padx=5)
        
        # Update function
        def update_color(c):
            entry.delete(0, "end")
            entry.insert(0, c)
            color_btn.configure(fg_color=c)
            style_dict[key] = c # Update internal dict immediately? Or on save? 
            # Better to update on save or bind events. For now, simple binding.

        def open_picker():
            color = colorchooser.askcolor(initialcolor=entry.get())
            if color[1]:
                update_color(color[1])

        color_btn.configure(command=open_picker)
        
        # Store refs to read values on save
        if "_style_widgets" not in item_ref:
            item_ref["_style_widgets"] = []
        item_ref["_style_widgets"].append((key, entry))

    def create_env_rows(self, parent, item):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=0, pady=0)
        item["_env_container"] = container
        
        env_data = item.get("env", [])
        if isinstance(env_data, dict):
            env_data = [env_data]
            item["_env_is_dict"] = True 
        else:
             item["_env_is_dict"] = False

        if not env_data:
            # Check if it was empty list or what
            pass 

        for env in env_data:
            self.add_single_env_row(container, env)

    def add_single_env_row(self, parent, env_val):
        row = ctk.CTkFrame(parent)
        row.pack(fill="x", pady=2)
        
        # Account
        acc_values = self.picklist_manager.get_account_display_list()
        current_acc_id = env_val.get("account", "")
        # Try to match ID to existing display name, else use ID
        current_acc_display = current_acc_id
        for val in acc_values:
            if self.picklist_manager.get_account_id_from_display(val) == current_acc_id:
                current_acc_display = val
                break
        
        # If the current ID not in list, add it to list temporarily for display? 
        # Or just show it. Combobox allows custom values if not state="readonly".
        # We leave it default so users can type new IDs too.
        
        acc_combo = ctk.CTkComboBox(row, values=acc_values, width=300)
        acc_combo.set(current_acc_display)
        acc_combo.pack(side="left", padx=5)
        row.acc_widget = acc_combo
        
        # Region
        reg_values = self.picklist_manager.regions
        current_reg = env_val.get("region", "")
        
        reg_combo = ctk.CTkComboBox(row, values=reg_values, width=150)
        reg_combo.set(current_reg)
        reg_combo.pack(side="left", padx=5)
        row.reg_widget = reg_combo
        
        # Delete button
        def delete_row():
            row.destroy()
            
        del_btn = ctk.CTkButton(row, text="X", width=30, fg_color="red", command=delete_row)
        del_btn.pack(side="right", padx=5)


    def save_config(self):
        if not self.filepath:
            return

        # Gather data from widgets
        try:
            clean_data = self.get_clean_config_data()

            # Save to file
            with open(self.filepath, 'w') as f:
                json_lib.dump(clean_data, f, indent=2)
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
            # Reload to refresh widgets/store new refs
            self.load_config(self.filepath)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def sync_widgets_to_data(self):
        """Syncs data from active widgets to the config_data model."""
        for item in self.config_data:
            # Update Env
            if "_env_container" in item:
                container = item["_env_container"]
                # Verify container still exists using string check on widget representation or try/except
                try:
                    if not container.winfo_exists():
                        continue
                except Exception:
                    continue

                new_envs = []
                for row in container.winfo_children():
                    if hasattr(row, "acc_widget") and hasattr(row, "reg_widget"):
                         try:
                             acc_display = row.acc_widget.get().strip()
                             reg = row.reg_widget.get().strip()
                             
                             acc_id = self.picklist_manager.get_account_id_from_display(acc_display)
                             if acc_id or reg:
                                 new_envs.append({"account": acc_id, "region": reg})
                         except Exception:
                             # Widget might be destroyed
                             pass
                
                if item.get("_env_is_dict", False) and len(new_envs) == 1:
                    item["env"] = new_envs[0]
                else:
                    item["env"] = new_envs
            
            # Update Styles
            if "_style_widgets" in item:
                if "style" not in item: item["style"] = {}
                for key, entry in item["_style_widgets"]:
                    try:
                         if entry.winfo_exists():
                            item["style"][key] = entry.get()
                    except Exception:
                        pass

    def get_clean_config_data(self):
        # First ensure model is up to date
        self.sync_widgets_to_data()
        
        clean_data = []
        for item in self.config_data:
            # Create clean copy without underscore keys
            clean_item = {k: v for k, v in item.items() if not k.startswith("_")}
            clean_data.append(clean_item)
            
        return clean_data

    def copy_to_clipboard(self):
        try:
            clean_data = self.get_clean_config_data()
            # Serialize indentation same as save
            json_str = json_lib.dumps(clean_data, indent=2)
            self.clipboard_clear()
            self.clipboard_append(json_str)
            messagebox.showinfo("Copied", "Configuration copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}")

    def apply_window_settings(self):
        loaded = False
        if os.path.exists(self.window_config_file):
            try:
                with open(self.window_config_file, 'r') as f:
                    config = json_lib.load(f)
                    width = config.get("width", 1100)
                    height = config.get("height", 700)
                    x = config.get("x", 100)
                    y = config.get("y", 100)
                    self.geometry(f"{width}x{height}+{x}+{y}")
                    loaded = True
            except Exception as e:
                print(f"Failed to load window config: {e}")
        
        if not loaded:
            # Default centering
            width = 1100
            height = 700
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.geometry(f"{width}x{height}+{x}+{y}")

    def generate_harmonious_colors(self):
        # Generate random hue
        h = random.random()
        # Saturation 0.5-0.9, Lightness 0.4-0.6 for nice UI colors
        s = 0.5 + random.random() * 0.4
        l = 0.4 + random.random() * 0.2
        
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        primary = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
        
        # Secondary: Complementary or Split Comp
        # Just simple shift for now
        h2 = (h + 0.5) % 1.0
        r2, g2, b2 = colorsys.hls_to_rgb(h2, l, s)
        secondary = '#%02x%02x%02x' % (int(r2*255), int(g2*255), int(b2*255))
        
        return primary, secondary

    def on_closing(self):
        try:
            # Save window state
            # self.geometry() returns string like "900x700+100+100"
            geo = self.geometry()
            parts = geo.split('+')
            size = parts[0].split('x')
            width = int(size[0])
            height = int(size[1])
            x = int(parts[1])
            y = int(parts[2])
            
            config = {
                "width": width,
                "height": height,
                "x": x,
                "y": y
            }
            with open(self.window_config_file, 'w') as f:
                json_lib.dump(config, f)
        except Exception as e:
            print(f"Failed to save window config: {e}")
            
        self.destroy()

if __name__ == "__main__":
    app = ConfiguratorApp()
    app.mainloop()
