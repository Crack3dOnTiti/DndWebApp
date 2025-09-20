#!/usr/bin/env python3
import os
import time
import sys
import subprocess
from database.models import create_tables
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database'))

load_dotenv()

def check_docker_status():
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, check=True)
        if 'dnd_postgres' in result.stdout and 'Up' in result.stdout:
            return True
        return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_database_connection():
    """Check if database is accessible"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            return False
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return True
    except:
        return False

def check_tables_exist():
    """Check if database tables are created"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            return False
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            count = result.fetchone()[0]
            return count > 0
    except:
        return False

def show_status():
    """Show current system status"""
    print("\nSystem Status:")
    print("=" * 40)
    # Docker status
    docker_status = check_docker_status()
    print(f"Docker Container:  {'Running' if docker_status else 'Not Running'}")

    # Database connection
    if docker_status:
        db_connection = check_database_connection()
        print(f"Database Access:   {'Connected' if db_connection else 'Failed'}")
        # Tables
        if db_connection:
            tables_exist = check_tables_exist()
            print(f"Database Tables:   {'Created' if tables_exist else 'Missing'}")
        else:
            print(f"Database Tables:   N/A (no connection)")
            print(f"Seed Data:         N/A (no connection)")
    else:
        print(f"Database Access:   N/A (Docker not running)")
        print(f"Database Tables:   N/A (Docker not running)")
        print(f"Seed Data:         N/A (Docker not running)")

def restart_docker():
    """Restart Docker containers with fresh data"""
    print("Restarting Docker containers...")
    try:
        print("Stopping containers and removing data...")
        subprocess.run(['docker-compose', 'down', '-v'], check=True)
        print("Starting fresh containers...")
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        print("Docker containers restarted successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart Docker: {e}")
        return False
    except FileNotFoundError:
        print("Docker Compose not found. Make sure Docker is installed.")
        return False

def setup_database():
    """Complete database setup with Docker restart"""
    print("Setting up database (full reset)...")
    # Factory reset docker
    if not restart_docker():
        return
    # Security sleep
    print("Waiting for database to initialize...")
    time.sleep(1.5)
    # Create tables
    try:
        create_tables()
    except Exception as e:
        print(f"Failed to create tables: {e}")
        return
    print("Database setup complete!")

def show_players():
    """Display all players in the database"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found")
            return
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT id, name, title, current_hp, max_hp, current_stam, max_stam, age, gender FROM players ORDER BY id"))
            players = result.fetchall()
            if players:
                print("\nPLAYERS:")
                print("-" * 80)
                print(f"{'ID':<3} {'Name':<20} {'Title':<15} {'HP':<12} {'Stamina':<12} {'Age':<4} {'Gender':<8}")
                print("-" * 80)
                for player in players:
                    hp_display = f"{player[3]}/{player[4]}"
                    stam_display = f"{player[5]}/{player[6]}"
                    age_display = player[7] if player[7] else "N/A"
                    gender_display = player[8] if player[8] else "N/A"
                    title_display = player[2] if player[2] else "No Title"
                    print(f"{player[0]:<3} {player[1]:<20} {title_display:<15} {hp_display:<12} {stam_display:<12} {age_display:<4} {gender_display:<8}")
            else:
                print("\nNo players found in database")
    except Exception as e:
        print(f"Failed to retrieve players: {e}")

def show_enemies():
    """Display all enemies in the database"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found")
            return
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT id, name, title, current_hp, max_hp, current_stam, max_stam, biology, main_style FROM enemies ORDER BY id"))
            enemies = result.fetchall()
            if enemies:
                print("\nENEMIES:")
                print("-" * 85)
                print(f"{'ID':<3} {'Name':<20} {'Title':<15} {'HP':<12} {'Stamina':<12} {'Biology':<10} {'Style':<15}")
                print("-" * 85)
                for enemy in enemies:
                    hp_display = f"{enemy[3]}/{enemy[4]}"
                    stam_display = f"{enemy[5]}/{enemy[6]}"
                    biology_display = enemy[7] if enemy[7] else "Unknown"
                    style_display = enemy[8] if enemy[8] else "No Style"
                    title_display = enemy[2] if enemy[2] else "No Title"
                    print(f"{enemy[0]:<3} {enemy[1]:<20} {title_display:<15} {hp_display:<12} {stam_display:<12} {biology_display:<10} {style_display:<15}")
            else:
                print("\nNo enemies found in database")
    except Exception as e:
        print(f"Failed to retrieve enemies: {e}")

def show_npcs():
    """Display all NPCs in the database"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found")
            return
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT id, name, title, current_hp, max_hp, general_feeling, starter_background, age FROM npcs ORDER BY id"))
            npcs = result.fetchall()
            if npcs:
                print("\nNPCs:")
                print("-" * 85)
                print(f"{'ID':<3} {'Name':<20} {'Title':<15} {'HP':<12} {'Feeling':<12} {'Background':<12} {'Age':<4}")
                print("-" * 85)
                for npc in npcs:
                    hp_display = f"{npc[3]}/{npc[4]}"
                    feeling_display = npc[5] if npc[5] else "Neutral"
                    background_display = npc[6] if npc[6] else "Unknown"
                    age_display = npc[7] if npc[7] else "N/A"
                    title_display = npc[2] if npc[2] else "No Title"
                    print(f"{npc[0]:<3} {npc[1]:<20} {title_display:<15} {hp_display:<12} {feeling_display:<12} {background_display:<12} {age_display:<4}")
            else:
                print("\nNo NPCs found in database")
    except Exception as e:
        print(f"Failed to retrieve NPCs: {e}")

def show_commands():
    """Show available commands"""
    print("\nAvailable commands:")
    print("  DataBase  - Full database setup (restart Docker + create tables + seed)")
    print("  reset     - Reset Docker containers (keeps existing data)")
    print("  status    - Show current system status")
    print("  players   - Show all players in database")
    print("  enemies   - Show all enemies in database") 
    print("  npcs      - Show all NPCs in database")
    print("  help      - Show this help message")
    print("  exit/quit/stop/kill/q/adios - Exit the program")

def okay():
    print("""   ⠀⠀⠀⠀⠀⠀⠀⠀⡇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⣷⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⢰⣿⣽⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠸⠟⠃⡙⢍⠿⠢⢄⣀⣠⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠘⢁⠂⢁⣦⡶⠟⠻⠉⠉⠂⠐⠂⠸⢀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠠⠂⣥⡾⠋⠀⠀⠀⠀⠀⣤⡄⠀⠀⠈⠂⠀⠀⠀⠀⠀⠀⠀
    ⠰⣶⣶⣶⣶⡄⠀⠀⠀⣹⠁⠀⡀⠄⠴⠾⠉⠁⠀⠀⠀⠀⠆⠀⠀⣼⡇⠀⠀⠀
    ⠀⠈⠛⠿⠃⠃⠄⠂⡇⠈⠠⠔⠒⠈⠁⢠⣶⣦⣀⣀⣠⠄⠀⠀⠘⡹⠿⠀⠀⠀
    ⠀⠀⠀⠀⠀⢀⠂⢀⠁⡄⠀⠀⠀⣀⣠⠾⣟⣻⣿⣯⡽⠂⠀⠀⠀⠘⠿⠆⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠌⢀⠃⠁⢾⣯⣭⣷⡿⠿⠗⠛⢁⠀⠀⠀⠀⡀⣾⣿⣿⣿⡄
    ⠀⠐⠃⠀⠀⠀⠈⢀⠎⠀⠀⡀⣀⢀⡀⡀⠠⠔⢊⠡⠀⠀⠀⠐⠠⠹⢿⠿⣻⡟
    ⠀⠀⠀⠀⠀⠄⠂⠁⠀⠀⠀⠀⠀⠀⠒⠒⠒⠋⠁⠀⠀⠀⠀⠠⢁⠂⣷⣿⣿⡟
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⠟⠉""")

def main():
    print("Type 'help' for available commands")

    while True:
        try:
            command = input("\n> ").strip()
            if command.lower() == "database":
                setup_database()
            elif command.lower() == "reset":
                restart_docker()
            elif command.lower() == "status":
                show_status()
            elif command.lower() == "players":
                show_players()
            elif command.lower() == "enemies":
                show_enemies()
            elif command.lower() == "npcs":
                show_npcs()
            elif command.lower() == "help":
                show_commands()
            elif command.lower() == "okay":
                okay()
            elif command.lower() in ["exit", "quit", "stop", "kill", "q", "adios"]:
                break
            elif command == "":
                continue
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()