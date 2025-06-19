"""
Tests for VEKA Profile system integration.
"""
import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.profile import Profile, ProfileDimensions, ThermalData, VEKASystem, ProfileType, STANDARD_PROFILES
from services.data_service import DataService
from services.service_container import container


class TestProfileModel:
    """Test Profile data model."""
    
    def test_profile_creation(self):
        """Test creating a profile with all data."""
        dimensions = ProfileDimensions(
            depth_mm=70.0,
            view_width_mm=119.0,
            rebate_height_mm=20.0,
            wall_thickness_mm=2.8,
            chamber_count=5,
            glazing_thickness_max=41.0
        )
        
        thermal = ThermalData(uf_value=1.3)
        
        profile = Profile(
            id="TEST_FRAME_70",
            system=VEKASystem.SOFTLINE_70,
            profile_type=ProfileType.FRAME,
            name="Test Blendrahmen",
            description="Test profile for validation",
            dimensions=dimensions,
            thermal=thermal
        )
        
        assert profile.id == "TEST_FRAME_70"
        assert profile.system == VEKASystem.SOFTLINE_70
        assert profile.profile_type == ProfileType.FRAME
        assert profile.dimensions.depth_mm == 70.0
        assert profile.thermal.uf_value == 1.3
        assert profile.display_name == "Softline 70 - Test Blendrahmen"
        assert profile.technical_code == "SL70_FRAME_70"
    
    def test_profile_to_dict(self):
        """Test profile serialization to dictionary."""
        profile = STANDARD_PROFILES[0]  # SL70_FRAME_70
        profile_dict = profile.to_dict()
        
        assert profile_dict['id'] == profile.id
        assert profile_dict['system_code'] == profile.system.code
        assert profile_dict['profile_type_code'] == profile.profile_type.code
        assert profile_dict['depth_mm'] == profile.dimensions.depth_mm
        assert profile_dict['uf_value'] == profile.thermal.uf_value
        assert 'Weiß' in profile_dict['standard_colors']
    
    def test_profile_from_dict(self):
        """Test profile deserialization from dictionary."""
        original = STANDARD_PROFILES[0]
        profile_dict = original.to_dict()
        
        restored = Profile.from_dict(profile_dict)
        
        assert restored.id == original.id
        assert restored.system == original.system
        assert restored.profile_type == original.profile_type
        assert restored.dimensions.depth_mm == original.dimensions.depth_mm
        assert restored.thermal.uf_value == original.thermal.uf_value
    
    def test_veka_systems(self):
        """Test VEKA system enumeration."""
        assert len(VEKASystem) >= 4
        
        sl70 = VEKASystem.SOFTLINE_70
        assert sl70.code == "SL70"
        assert sl70.display_name == "Softline 70"
        assert sl70.depth_mm == 70
        
        sl82 = VEKASystem.SOFTLINE_82
        assert sl82.code == "SL82"
        assert sl82.depth_mm == 82
    
    def test_profile_types(self):
        """Test profile type enumeration."""
        assert len(ProfileType) >= 5
        
        frame = ProfileType.FRAME
        assert frame.code == "frame"
        assert frame.display_name == "Blendrahmen"
        
        sash = ProfileType.SASH
        assert sash.code == "sash"
        assert sash.display_name == "Flügel"


class TestDataServiceProfiles:
    """Test DataService profile operations."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        return temp_file.name
    
    @pytest.fixture
    def data_service(self, temp_db):
        """Create DataService with temporary database."""
        service = DataService(temp_db)
        yield service
        service.shutdown()
        try:
            os.unlink(temp_db)
        except:
            pass
    
    def test_profile_save_and_load(self, data_service):
        """Test saving and loading profiles."""
        # Create test profile
        dimensions = ProfileDimensions(
            depth_mm=82.0,
            view_width_mm=127.0,
            rebate_height_mm=24.0,
            wall_thickness_mm=3.0,
            chamber_count=6,
            glazing_thickness_max=53.0
        )
        
        thermal = ThermalData(uf_value=1.0)
        
        profile = Profile(
            id="TEST_SL82_FRAME_82",
            system=VEKASystem.SOFTLINE_82,
            profile_type=ProfileType.FRAME,
            name="Test Blendrahmen 82mm",
            description="Test profile for SL82",
            dimensions=dimensions,
            thermal=thermal
        )
        
        # Save profile
        profile_id = data_service.save_profile(profile)
        assert profile_id == "TEST_SL82_FRAME_82"
        
        # Load profile
        loaded_profile = data_service.get_profile(profile_id)
        assert loaded_profile is not None
        assert loaded_profile.id == profile.id
        assert loaded_profile.system == profile.system
        assert loaded_profile.dimensions.depth_mm == profile.dimensions.depth_mm
        assert loaded_profile.thermal.uf_value == profile.thermal.uf_value
    
    def test_standard_profiles_loaded(self, data_service):
        """Test that standard profiles are automatically loaded."""
        profiles = data_service.get_profiles()
        
        # Should have at least the standard profiles
        assert len(profiles) >= len(STANDARD_PROFILES)
        
        # Check specific standard profiles exist
        profile_ids = {p.id for p in profiles}
        for std_profile in STANDARD_PROFILES:
            assert std_profile.id in profile_ids
    
    def test_get_profiles_by_system(self, data_service):
        """Test filtering profiles by system."""
        sl70_profiles = data_service.get_profiles(system_code="SL70")
        sl82_profiles = data_service.get_profiles(system_code="SL82")
        
        assert len(sl70_profiles) >= 1
        assert len(sl82_profiles) >= 1
        
        # All SL70 profiles should have SL70 system
        for profile in sl70_profiles:
            assert profile.system.code == "SL70"
        
        # All SL82 profiles should have SL82 system
        for profile in sl82_profiles:
            assert profile.system.code == "SL82"
    
    def test_get_profiles_by_type(self, data_service):
        """Test filtering profiles by type."""
        frame_profiles = data_service.get_profiles(profile_type_code="frame")
        sash_profiles = data_service.get_profiles(profile_type_code="sash")
        
        assert len(frame_profiles) >= 1
        assert len(sash_profiles) >= 1
        
        # All frame profiles should be frames
        for profile in frame_profiles:
            assert profile.profile_type.code == "frame"
        
        # All sash profiles should be sashes
        for profile in sash_profiles:
            assert profile.profile_type.code == "sash"
    
    def test_list_profile_names(self, data_service):
        """Test getting profile names for UI dropdowns."""
        names = data_service.list_profile_names()
        
        assert len(names) >= len(STANDARD_PROFILES)
        assert all(isinstance(name, str) for name in names)
        
        # Should contain standard profile names
        name_string = " ".join(names)
        assert "Softline 70" in name_string
        assert "Softline 82" in name_string
    
    def test_profile_caching(self, data_service):
        """Test profile memory caching."""
        # First load - should hit database
        profile1 = data_service.get_profile("SL70_FRAME_70")
        assert profile1 is not None
        
        # Second load - should hit cache
        profile2 = data_service.get_profile("SL70_FRAME_70")
        assert profile2 is not None
        assert profile1.id == profile2.id
        
        # Clear cache and reload - should hit database again
        data_service.clear_profile_cache()
        profile3 = data_service.get_profile("SL70_FRAME_70")
        assert profile3 is not None
        assert profile3.id == profile1.id


class TestProfileSystemIntegration:
    """Test profile system integration with ElementDesigner."""
    
    def test_profile_loaded(self):
        """Test specific profile loading."""
        # Create temporary DataService
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        try:
            data_service = DataService(temp_file.name)
            
            # Test loading specific profile
            profile = data_service.get_profile("SL82_FRAME_82")
            assert profile is not None
            assert profile.dimensions.depth_mm == 82
            assert profile.thermal.uf_value < 1.1  # Should be 1.0
            
            data_service.shutdown()
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    def test_designer_profile_integration(self):
        """Test ElementDesigner can access profiles."""
        # Mock DataService
        mock_data_service = Mock()
        mock_data_service.get_profiles.return_value = STANDARD_PROFILES
        
        # Test that ElementDesigner classes can be imported and have profile support
        from views.element_designer_view import ElementDesignerView
        
        # Test class has required attributes for profile support
        assert hasattr(ElementDesignerView, 'profile_changed')
        assert hasattr(ElementDesignerView, '__init__')
        
        # Mock container for profile access test
        with patch('services.service_container.container') as mock_container:
            mock_container.get.return_value = mock_data_service
            
            # Test profile loading method exists
            # (We can't instantiate GUI components without QApplication)
            designer_class = ElementDesignerView
            assert hasattr(designer_class, '_load_profile_systems')
            assert hasattr(designer_class, '_on_profile_changed')
    
    def test_profile_performance(self):
        """Test profile loading performance."""
        import time
        
        # Create temporary DataService
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        try:
            data_service = DataService(temp_file.name)
            
            # Time profile loading
            start_time = time.time()
            profiles = data_service.get_profiles()
            load_time = time.time() - start_time
            
            # Should load quickly (< 300ms as per requirements)
            assert load_time < 0.3
            assert len(profiles) > 0
            
            # Time cached access
            start_time = time.time()
            profile = data_service.get_profile("SL70_FRAME_70")
            cache_time = time.time() - start_time
            
            # Cached access should be very fast
            assert cache_time < 0.01
            assert profile is not None
            
            data_service.shutdown()
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])