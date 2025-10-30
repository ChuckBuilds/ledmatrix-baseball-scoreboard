from unittest import TestCase

from src.plugin_system.base_plugin import BasePlugin


class DummyPlugin(BasePlugin):
    """Test plugin implementation."""
    
    def update(self):
        """Required abstract method."""
        pass

    def display(self, force_clear: bool = False):
        """Required abstract method."""
        pass


class TestBasePluginConfigChange(TestCase):
    """Test on_config_change hook in BasePlugin."""
    
    def test_on_config_change_updates_internal_state(self):
        """Test that on_config_change updates plugin state."""
        p = DummyPlugin(
            plugin_id="dummy",
            config={"enabled": False, "display_duration": 10},
            display_manager=None,
            cache_manager=None,
            plugin_manager=None,
        )
        
        self.assertFalse(p.enabled)
        self.assertEqual(p.get_display_duration(), 10)

        # Change config via hook
        new_cfg = {"enabled": True, "display_duration": 25, "transition": {"type": "redraw"}}
        p.on_config_change(new_cfg)

        # Verify state updated
        self.assertTrue(p.enabled)
        self.assertEqual(p.get_display_duration(), 25)
        self.assertEqual(p.config, new_cfg)
    
    def test_on_config_change_updates_enabled_flag(self):
        """Test that enabled flag is updated correctly."""
        p = DummyPlugin(
            plugin_id="dummy",
            config={"enabled": True},
            display_manager=None,
            cache_manager=None,
            plugin_manager=None,
        )
        
        self.assertTrue(p.enabled)
        
        # Disable via config change
        p.on_config_change({"enabled": False})
        self.assertFalse(p.enabled)
        
        # Re-enable
        p.on_config_change({"enabled": True})
        self.assertTrue(p.enabled)
    
    def test_on_config_change_with_nested_config(self):
        """Test config change with nested configuration."""
        p = DummyPlugin(
            plugin_id="dummy",
            config={"enabled": True, "settings": {"key1": "value1"}},
            display_manager=None,
            cache_manager=None,
            plugin_manager=None,
        )
        
        # Update with nested config
        new_cfg = {
            "enabled": False,
            "settings": {"key1": "updated", "key2": "new"}
        }
        p.on_config_change(new_cfg)
        
        self.assertFalse(p.enabled)
        self.assertEqual(p.config["settings"]["key1"], "updated")
        self.assertEqual(p.config["settings"]["key2"], "new")
