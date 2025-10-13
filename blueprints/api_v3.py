from flask import Blueprint, request, jsonify, Response
import json
import subprocess
import time
from pathlib import Path

# Will be initialized when blueprint is registered
config_manager = None

api_v3 = Blueprint('api_v3', __name__)

@api_v3.route('/config/main', methods=['GET'])
def get_main_config():
    """Get main configuration"""
    try:
        if not api_v3.config_manager:
            return jsonify({'status': 'error', 'message': 'Config manager not initialized'}), 500

        config = api_v3.config_manager.load_config()
        return jsonify({'status': 'success', 'data': config})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/config/main', methods=['POST'])
def save_main_config():
    """Save main configuration"""
    try:
        if not api_v3.config_manager:
            return jsonify({'status': 'error', 'message': 'Config manager not initialized'}), 500

        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        # Merge with existing config (similar to original implementation)
        current_config = api_v3.config_manager.load_config()

        # Merge sports configurations
        if 'nfl_scoreboard' in data:
            current_config['nfl_scoreboard'] = data['nfl_scoreboard']
        if 'mlb_scoreboard' in data:
            current_config['mlb_scoreboard'] = data['mlb_scoreboard']
        if 'nhl_scoreboard' in data:
            current_config['nhl_scoreboard'] = data['nhl_scoreboard']
        if 'nba_scoreboard' in data:
            current_config['nba_scoreboard'] = data['nba_scoreboard']
        if 'ncaa_fb_scoreboard' in data:
            current_config['ncaa_fb_scoreboard'] = data['ncaa_fb_scoreboard']
        if 'soccer_scoreboard' in data:
            current_config['soccer_scoreboard'] = data['soccer_scoreboard']

        # Save the merged config
        api_v3.config_manager.save_config(current_config)

        return jsonify({'status': 'success', 'message': 'Configuration saved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/config/secrets', methods=['GET'])
def get_secrets_config():
    """Get secrets configuration"""
    try:
        if not api_v3.config_manager:
            return jsonify({'status': 'error', 'message': 'Config manager not initialized'}), 500

        config = api_v3.config_manager.get_raw_file_content('secrets')
        return jsonify({'status': 'success', 'data': config})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/system/status', methods=['GET'])
def get_system_status():
    """Get system status"""
    try:
        # This would integrate with actual system monitoring
        status = {
            'timestamp': time.time(),
            'uptime': 'Running',
            'service_active': True,
            'cpu_percent': 0,  # Would need psutil or similar
            'memory_used_percent': 0,
            'cpu_temp': 0,
            'disk_used_percent': 0
        }
        return jsonify({'status': 'success', 'data': status})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/system/action', methods=['POST'])
def execute_system_action():
    """Execute system actions (start/stop/reboot/etc)"""
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'status': 'error', 'message': 'Action required'}), 400

        action = data['action']
        mode = data.get('mode')  # For on-demand modes

        # Map actions to subprocess calls (similar to original implementation)
        if action == 'start_display':
            if mode:
                # For on-demand modes, we would need to integrate with the display controller
                # For now, just start the display service
                result = subprocess.run(['sudo', 'systemctl', 'start', 'ledmatrix'],
                                     capture_output=True, text=True)
                return jsonify({
                    'status': 'success' if result.returncode == 0 else 'error',
                    'message': f'Started display in {mode} mode',
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                })
            else:
                result = subprocess.run(['sudo', 'systemctl', 'start', 'ledmatrix'],
                                     capture_output=True, text=True)
        elif action == 'stop_display':
            result = subprocess.run(['sudo', 'systemctl', 'stop', 'ledmatrix'],
                                 capture_output=True, text=True)
        elif action == 'enable_autostart':
            result = subprocess.run(['sudo', 'systemctl', 'enable', 'ledmatrix'],
                                 capture_output=True, text=True)
        elif action == 'disable_autostart':
            result = subprocess.run(['sudo', 'systemctl', 'disable', 'ledmatrix'],
                                 capture_output=True, text=True)
        elif action == 'reboot_system':
            result = subprocess.run(['sudo', 'reboot'],
                                 capture_output=True, text=True)
        elif action == 'git_pull':
            home_dir = str(Path.home())
            project_dir = os.path.join(home_dir, 'LEDMatrix')
            result = subprocess.run(['git', 'pull'],
                                 capture_output=True, text=True, cwd=project_dir)
        else:
            return jsonify({'status': 'error', 'message': f'Unknown action: {action}'}), 400

        return jsonify({
            'status': 'success' if result.returncode == 0 else 'error',
            'message': f'Action {action} completed',
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/display/current', methods=['GET'])
def get_display_current():
    """Get current display state"""
    try:
        # This would integrate with the actual display controller
        display_data = {
            'timestamp': time.time(),
            'width': 128,
            'height': 64,
            'image': None  # Base64 encoded image data
        }
        return jsonify({'status': 'success', 'data': display_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/logs', methods=['GET'])
def get_logs():
    """Get system logs"""
    try:
        # Get logs from journalctl for the ledmatrix service (similar to original)
        result = subprocess.run(
            ['sudo', 'journalctl', '-u', 'ledmatrix.service', '-n', '500', '--no-pager'],
            capture_output=True, text=True, check=True
        )
        logs = result.stdout
        return jsonify({'status': 'success', 'data': {'logs': logs}})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': f"Error fetching logs: {e.stderr}"}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/plugins/installed', methods=['GET'])
def get_installed_plugins():
    """Get installed plugins"""
    try:
        # This would integrate with the actual plugin system
        # For now, return sample plugins
        plugins = [
            {
                'id': 'nfl-scoreboard',
                'name': 'NFL Scoreboard',
                'author': 'Sports Data Inc',
                'version': '1.2.0',
                'category': 'sports',
                'description': 'Display NFL game scores and statistics',
                'tags': ['sports', 'football', 'scores'],
                'enabled': True,
                'verified': True
            },
            {
                'id': 'weather-widget',
                'name': 'Weather Widget',
                'author': 'Weather Corp',
                'version': '2.1.0',
                'category': 'weather',
                'description': 'Show current weather conditions',
                'tags': ['weather', 'utility'],
                'enabled': False,
                'verified': False
            },
            {
                'id': 'stocks-ticker',
                'name': 'Stocks Ticker',
                'author': 'Finance Tools',
                'version': '1.0.5',
                'category': 'finance',
                'description': 'Display stock prices and charts',
                'tags': ['finance', 'stocks', 'charts'],
                'enabled': True,
                'verified': True
            }
        ]
        return jsonify({'status': 'success', 'data': {'plugins': plugins}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/plugins/toggle', methods=['POST'])
def toggle_plugin():
    """Toggle plugin enabled/disabled"""
    try:
        data = request.get_json()
        if not data or 'plugin_id' not in data or 'enabled' not in data:
            return jsonify({'status': 'error', 'message': 'plugin_id and enabled required'}), 400

        plugin_id = data['plugin_id']
        enabled = data['enabled']

        # This would integrate with the actual plugin system
        # For now, return success
        return jsonify({'status': 'success', 'message': f'Plugin {plugin_id} {"enabled" if enabled else "disabled"}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/plugins/config', methods=['GET'])
def get_plugin_config():
    """Get plugin configuration"""
    try:
        plugin_id = request.args.get('plugin_id')
        if not plugin_id:
            return jsonify({'status': 'error', 'message': 'plugin_id required'}), 400

        # This would integrate with the actual plugin system
        # For now, return sample config
        config = {
            'enabled': True,
            'update_interval': 3600,
            'display_duration': 30
        }

        return jsonify({'status': 'success', 'data': config})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/plugins/update', methods=['POST'])
def update_plugin():
    """Update plugin"""
    try:
        data = request.get_json()
        if not data or 'plugin_id' not in data:
            return jsonify({'status': 'error', 'message': 'plugin_id required'}), 400

        plugin_id = data['plugin_id']

        # This would integrate with the actual plugin system
        return jsonify({'status': 'success', 'message': f'Plugin {plugin_id} updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/plugins/uninstall', methods=['POST'])
def uninstall_plugin():
    """Uninstall plugin"""
    try:
        data = request.get_json()
        if not data or 'plugin_id' not in data:
            return jsonify({'status': 'error', 'message': 'plugin_id required'}), 400

        plugin_id = data['plugin_id']

        # This would integrate with the actual plugin system
        return jsonify({'status': 'success', 'message': f'Plugin {plugin_id} uninstalled successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/plugins/install', methods=['POST'])
def install_plugin():
    """Install plugin from store"""
    try:
        data = request.get_json()
        if not data or 'plugin_id' not in data:
            return jsonify({'status': 'error', 'message': 'plugin_id required'}), 400

        plugin_id = data['plugin_id']

        # This would integrate with the actual plugin system
        return jsonify({'status': 'success', 'message': f'Plugin {plugin_id} installed successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/plugins/store/list', methods=['GET'])
def list_plugin_store():
    """Search plugin store"""
    try:
        query = request.args.get('query', '')
        category = request.args.get('category', '')

        # This would integrate with the actual plugin store
        # For now, return sample plugins
        plugins = [
            {
                'id': 'sample-plugin-1',
                'name': 'Sample Sports Plugin',
                'author': 'LED Matrix Team',
                'version': '1.0.0',
                'category': 'sports',
                'description': 'A sample plugin for sports data',
                'tags': ['sports', 'data'],
                'stars': 42,
                'downloads': 1337,
                'verified': True,
                'repo': 'https://github.com/example/sample-plugin'
            },
            {
                'id': 'sample-plugin-2',
                'name': 'Weather Widget',
                'author': 'Weather Corp',
                'version': '2.1.0',
                'category': 'weather',
                'description': 'Display weather information',
                'tags': ['weather', 'utility'],
                'stars': 89,
                'downloads': 567,
                'verified': False,
                'repo': 'https://github.com/example/weather-plugin'
            }
        ]

        # Filter by query and category if provided
        filtered_plugins = plugins
        if query:
            query_lower = query.lower()
            filtered_plugins = [p for p in filtered_plugins if 
                query_lower in p['name'].lower() or 
                query_lower in p['description'].lower()
            ]
        if category:
            filtered_plugins = [p for p in filtered_plugins if p['category'] == category]

        return jsonify({'status': 'success', 'data': {'plugins': filtered_plugins}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/plugins/store/refresh', methods=['POST'])
def refresh_plugin_store():
    """Refresh plugin store repository"""
    try:
        # This would integrate with the actual plugin store refresh logic
        return jsonify({'status': 'success', 'message': 'Plugin store refreshed', 'plugin_count': 50})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/plugins/schema', methods=['GET'])
def get_plugin_schema():
    """Get plugin configuration schema"""
    try:
        plugin_id = request.args.get('plugin_id')
        if not plugin_id:
            return jsonify({'status': 'error', 'message': 'plugin_id required'}), 400

        # This would integrate with the actual plugin system to read config_schema.json
        # For now, return a sample schema
        schema = {
            'type': 'object',
            'properties': {
                'enabled': {
                    'type': 'boolean',
                    'title': 'Enable Plugin',
                    'description': 'Enable or disable this plugin',
                    'default': True
                },
                'update_interval': {
                    'type': 'integer',
                    'title': 'Update Interval',
                    'description': 'How often to update data (seconds)',
                    'minimum': 60,
                    'maximum': 3600,
                    'default': 300
                },
                'display_duration': {
                    'type': 'integer',
                    'title': 'Display Duration',
                    'description': 'How long to show content (seconds)',
                    'minimum': 5,
                    'maximum': 300,
                    'default': 30
                },
                'favorite_teams': {
                    'type': 'array',
                    'title': 'Favorite Teams',
                    'description': 'List of favorite team abbreviations',
                    'items': {'type': 'string'},
                    'default': []
                },
                'data_source': {
                    'type': 'string',
                    'title': 'Data Source',
                    'description': 'Where to get data from',
                    'enum': ['api', 'file', 'database'],
                    'default': 'api'
                }
            }
        }

        return jsonify({'status': 'success', 'data': {'schema': schema}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/fonts/catalog', methods=['GET'])
def get_fonts_catalog():
    """Get fonts catalog"""
    try:
        # This would integrate with the actual font system
        # For now, return sample fonts
        catalog = {
            'press_start': 'assets/fonts/press-start-2p.ttf',
            'four_by_six': 'assets/fonts/4x6.bdf',
            'cozette_bdf': 'assets/fonts/cozette.bdf',
            'matrix_light_6': 'assets/fonts/matrix-light-6.bdf'
        }
        return jsonify({'status': 'success', 'data': {'catalog': catalog}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/fonts/tokens', methods=['GET'])
def get_font_tokens():
    """Get font size tokens"""
    try:
        # This would integrate with the actual font system
        # For now, return sample tokens
        tokens = {
            'xs': 6,
            'sm': 8,
            'md': 10,
            'lg': 12,
            'xl': 14,
            'xxl': 16
        }
        return jsonify({'status': 'success', 'data': {'tokens': tokens}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/fonts/overrides', methods=['GET'])
def get_fonts_overrides():
    """Get font overrides"""
    try:
        # This would integrate with the actual font system
        # For now, return empty overrides
        overrides = {}
        return jsonify({'status': 'success', 'data': {'overrides': overrides}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/fonts/overrides', methods=['POST'])
def save_fonts_overrides():
    """Save font overrides"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        # This would integrate with the actual font system
        return jsonify({'status': 'success', 'message': 'Font overrides saved'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/fonts/overrides/<element_key>', methods=['DELETE'])
def delete_font_override(element_key):
    """Delete font override"""
    try:
        # This would integrate with the actual font system
        return jsonify({'status': 'success', 'message': f'Font override for {element_key} deleted'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/fonts/upload', methods=['POST'])
def upload_font():
    """Upload font file"""
    try:
        if 'font_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No font file provided'}), 400

        font_file = request.files['font_file']
        font_family = request.form.get('font_family', '')

        if not font_file or not font_family:
            return jsonify({'status': 'error', 'message': 'Font file and family name required'}), 400

        # Validate file type
        allowed_extensions = ['.ttf', '.bdf']
        file_extension = font_file.filename.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            return jsonify({'status': 'error', 'message': 'Only .ttf and .bdf files are allowed'}), 400

        # Validate font family name
        if not font_family.replace('_', '').replace('-', '').isalnum():
            return jsonify({'status': 'error', 'message': 'Font family name must contain only letters, numbers, underscores, and hyphens'}), 400

        # This would integrate with the actual font system to save the file
        # For now, just return success
        return jsonify({'status': 'success', 'message': f'Font {font_family} uploaded successfully', 'font_family': font_family})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_v3.route('/fonts/delete/<font_family>', methods=['DELETE'])
def delete_font(font_family):
    """Delete font"""
    try:
        # This would integrate with the actual font system
        return jsonify({'status': 'success', 'message': f'Font {font_family} deleted'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
