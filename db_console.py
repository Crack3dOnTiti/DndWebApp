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
    """Display all players - just ID and name"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found")
            return
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT id, name FROM players ORDER BY id"))
            players = result.fetchall()
            if players:
                print("\n🎲 PLAYERS:")
                print("-" * 30)
                print(f"{'ID':<5} {'Name':<20}")
                print("-" * 30)
                for player in players:
                    print(f"{player[0]:<5} {player[1]:<20}")
            else:
                print("\n🎲 No players found in database")
    except Exception as e:
        print(f"Failed to retrieve players: {e}")

def show_enemies():
    """Display all enemies - just ID and name"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found")
            return
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT id, name FROM enemies ORDER BY id"))
            enemies = result.fetchall()
            if enemies:
                print("\n⚔️  ENEMIES:")
                print("-" * 30)
                print(f"{'ID':<5} {'Name':<20}")
                print("-" * 30)
                for enemy in enemies:
                    print(f"{enemy[0]:<5} {enemy[1]:<20}")
            else:
                print("\n⚔️  No enemies found in database")
    except Exception as e:
        print(f"Failed to retrieve enemies: {e}")

def show_npcs():
    """Display all NPCs - just ID and name"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found")
            return
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT id, name FROM npcs ORDER BY id"))
            npcs = result.fetchall()
            if npcs:
                print("\n👥 NPCs:")
                print("-" * 30)
                print(f"{'ID':<5} {'Name':<20}")
                print("-" * 30)
                for npc in npcs:
                    print(f"{npc[0]:<5} {npc[1]:<20}")
            else:
                print("\n👥 No NPCs found in database")
    except Exception as e:
        print(f"Failed to retrieve NPCs: {e}")

def show_player_detail(player_id):
    """Display detailed information for a specific player"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found")
            return
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            # Get player info
            player_result = connection.execute(text("SELECT * FROM players WHERE id = :id"), {"id": player_id})
            player = player_result.fetchone()
            
            if not player:
                print(f"Player with ID {player_id} not found")
                return
            
            # Get player stats
            stats_result = connection.execute(text("SELECT * FROM player_stats WHERE player_id = :id"), {"id": player_id})
            stats = stats_result.fetchone()
            
            # Correct column mapping based on your model:
            # 0=id, 1=current_hp, 2=max_hp, 3=current_stam, 4=max_stam, 5=name, 6=title, 7=sin, 8=virtue, 
            # 9=general_feeling, 10=skill_name, 11=skill_description, 12=passive_name, 13=passive_description,
            # 14=starter_background, 15=age, 16=gender, 17=temperature, 18=saturation, 19=biology, 
            # 20=main_style, 21=ritual, 22=last_d5_roll, 23=last_d10_roll, 24=last_d20_roll, 25=last_d100_roll
            
            print(f"\n🎲 PLAYER DETAILS - ID: {player_id}")
            print("=" * 60)
            print(f"Name: {player[5]}")
            print(f"Title: {player[6] or 'No Title'}")
            print(f"Age: {player[15]} | Gender: {player[16]}")
            print(f"Biology: {player[19]} | Background: {player[14] or 'Unknown'}")
            print()
            print("HEALTH & RESOURCES:")
            print(f"  HP: {player[1]}/{player[2]} | Stamina: {player[3]}/{player[4]}")
            print(f"  Temperature: {player[17] or 'Normal'} | Saturation: {player[18]}")
            print()
            print("CHARACTER TRAITS:")
            print(f"  Sin: {player[7] or 'None'} | Virtue: {player[8] or 'None'}")
            print(f"  General Feeling: {player[9]}")
            print(f"  Main Style: {player[20] or 'None'} | Ritual: {player[21]}")
            print()
            print("ABILITIES:")
            print(f"  Skill: {player[10] or 'None'}")
            if player[11]:
                print(f"    Description: {player[11]}")
            print(f"  Passive: {player[12] or 'None'}")
            if player[13]:
                print(f"    Description: {player[13]}")
            print()
            print("DICE ROLLS:")
            print(f"  Last d5: {player[22] or 'None'} | Last d10: {player[23] or 'None'}")
            print(f"  Last d20: {player[24] or 'None'} | Last d100: {player[25] or 'None'}")
            
            if stats:
                print()
                print("STATS:")
                print(f"  STR: {stats[2]} | STM: {stats[3]} | SPD: {stats[4]}")
                print(f"  LUK: {stats[5]} | MNY: {stats[6]}x")
            else:
                print("\nSTATS: No stats found")
                
    except Exception as e:
        print(f"Failed to retrieve player details: {e}")

def show_enemy_detail(enemy_id):
    """Display detailed information for a specific enemy"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found")
            return
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            # Get enemy info
            enemy_result = connection.execute(text("SELECT * FROM enemies WHERE id = :id"), {"id": enemy_id})
            enemy = enemy_result.fetchone()
            
            if not enemy:
                print(f"Enemy with ID {enemy_id} not found")
                return
            
            # Get enemy stats
            stats_result = connection.execute(text("SELECT * FROM enemy_stats WHERE enemy_id = :id"), {"id": enemy_id})
            stats = stats_result.fetchone()
            
            print(f"\n⚔️  ENEMY DETAILS - ID: {enemy_id}")
            print("=" * 60)
            print(f"Name: {enemy[5]}")
            print(f"Title: {enemy[6] or 'No Title'}")
            print(f"Age: {enemy[10] or 'Unknown'} | Gender: {enemy[11]}")
            print(f"Biology: {enemy[12]} | Main Style: {enemy[13] or 'None'}")
            print()
            print("HEALTH:")
            print(f"  HP: {enemy[1]}/{enemy[2]} | Stamina: {enemy[3]}/{enemy[4]}")
            print()
            print("CHARACTER TRAITS:")
            print(f"  Sin: {enemy[7] or 'None'} | Virtue: {enemy[8] or 'None'}")
            print(f"  Ritual: {enemy[14]}")
            print()
            print("ABILITIES:")
            print(f"  Skill: {enemy[9] or 'None'}")
            print()
            print("DICE ROLLS:")
            print(f"  Last d5: {enemy[15] or 'None'} | Last d10: {enemy[16] or 'None'}")
            print(f"  Last d20: {enemy[17] or 'None'} | Last d100: {enemy[18] or 'None'}")
            
            if stats:
                print()
                print("STATS:")
                print(f"  STR: {stats[2]} | STM: {stats[3]} | SPD: {stats[4]}")
                print(f"  LUK: {stats[5]} | MNY: {stats[6]}x")
            else:
                print("\nSTATS: No stats found")
                
    except Exception as e:
        print(f"Failed to retrieve enemy details: {e}")

def show_npc_detail(npc_id):
    """Display detailed information for a specific NPC"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found")
            return
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            # Get NPC info
            npc_result = connection.execute(text("SELECT * FROM npcs WHERE id = :id"), {"id": npc_id})
            npc = npc_result.fetchone()
            
            if not npc:
                print(f"NPC with ID {npc_id} not found")
                return
            
            # Get NPC stats
            stats_result = connection.execute(text("SELECT * FROM npc_stats WHERE npc_id = :id"), {"id": npc_id})
            stats = stats_result.fetchone()
            
            print(f"\n👥 NPC DETAILS - ID: {npc_id}")
            print("=" * 60)
            print(f"Name: {npc[5]}")
            print(f"Title: {npc[6] or 'No Title'}")
            print(f"Age: {npc[10] or 'Unknown'} | Gender: {npc[11]}")
            print(f"Biology: {npc[12]} | Main Style: {npc[13] or 'None'}")
            print()
            print("HEALTH:")
            print(f"  HP: {npc[1]}/{npc[2]} | Stamina: {npc[3]}/{npc[4]}")
            print()
            print("CHARACTER TRAITS:")
            print(f"  Sin: {npc[7] or 'None'} | Virtue: {npc[8] or 'None'}")
            print(f"  Ritual: {npc[14]}")
            print()
            print("ABILITIES:")
            print(f"  Skill: {npc[9] or 'None'}")
            print()
            print("DICE ROLLS:")
            print(f"  Last d5: {npc[15] or 'None'} | Last d10: {npc[16] or 'None'}")
            print(f"  Last d20: {npc[17] or 'None'} | Last d100: {npc[18] or 'None'}")
            
            if stats:
                print()
                print("STATS:")
                print(f"  STR: {stats[2]} | STM: {stats[3]} | SPD: {stats[4]}")
                print(f"  LUK: {stats[5]} | MNY: {stats[6]}x")
            else:
                print("\nSTATS: No stats found")
                
    except Exception as e:
        print(f"Failed to retrieve NPC details: {e}")

def show_commands():
    """Show available commands"""
    print("\nAvailable commands:")
    print("  database  - Full database setup (restart Docker + create tables)")
    print("  reset     - Reset Docker containers (keeps existing data)")
    print("  status    - Show current system status")
    print("  players   - Show all players (ID and name)")
    print("  enemies   - Show all enemies (ID and name)")
    print("  npcs      - Show all NPCs (ID and name)")
    print("  player X  - Show detailed info for player with ID X")
    print("  enemy X   - Show detailed info for enemy with ID X")
    print("  npc X     - Show detailed info for NPC with ID X")
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
            elif command.lower().startswith("player "):
                try:
                    player_id = int(command.split()[1])
                    show_player_detail(player_id)
                except (IndexError, ValueError):
                    print("Usage: player <ID>")
            elif command.lower().startswith("enemy "):
                try:
                    enemy_id = int(command.split()[1])
                    show_enemy_detail(enemy_id)
                except (IndexError, ValueError):
                    print("Usage: enemy <ID>")
            elif command.lower().startswith("npc "):
                try:
                    npc_id = int(command.split()[1])
                    show_npc_detail(npc_id)
                except (IndexError, ValueError):
                    print("Usage: npc <ID>")
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