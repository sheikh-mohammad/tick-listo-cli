"""Unit tests for IDManager - Auto-incrementing ID management."""

import pytest

from tick_listo_cli.services.id_manager import IDManager


class TestIDGeneration:
    """Test ID generation and increment."""

    def test_first_id_is_one(self):
        """Test that first generated ID is 1."""
        id_manager = IDManager()
        task_id = id_manager.generate_id()
        assert task_id == 1

    def test_sequential_id_generation(self):
        """Test that IDs increment sequentially."""
        id_manager = IDManager()

        id1 = id_manager.generate_id()
        id2 = id_manager.generate_id()
        id3 = id_manager.generate_id()

        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    def test_generate_multiple_ids(self):
        """Test generating multiple IDs in sequence."""
        id_manager = IDManager()

        ids = [id_manager.generate_id() for _ in range(10)]

        assert ids == list(range(1, 11))

    def test_ids_are_never_reused(self):
        """Test that IDs are never reused during normal operation."""
        id_manager = IDManager()

        # Generate some IDs
        id1 = id_manager.generate_id()
        id2 = id_manager.generate_id()
        id3 = id_manager.generate_id()

        # Even if we don't use them, next ID should be 4
        id4 = id_manager.generate_id()

        assert id4 == 4
        assert id4 not in [id1, id2, id3]


class TestCounterManagement:
    """Test ID counter persistence and management."""

    def test_get_current_counter_without_incrementing(self):
        """Test getting current counter value without incrementing."""
        id_manager = IDManager()

        # Generate one ID
        id_manager.generate_id()  # Returns 1

        # Get current counter (should be 2, the next ID to generate)
        current = id_manager.get_current_counter()
        assert current == 2

        # Verify counter wasn't incremented
        next_id = id_manager.generate_id()
        assert next_id == 2

    def test_get_current_counter_initial_state(self):
        """Test getting counter in initial state."""
        id_manager = IDManager()

        current = id_manager.get_current_counter()
        assert current == 1

    def test_set_counter_to_specific_value(self):
        """Test setting counter to specific value."""
        id_manager = IDManager()

        id_manager.set_counter(10)

        next_id = id_manager.generate_id()
        assert next_id == 10

    def test_set_counter_with_zero_raises_value_error(self):
        """Test that setting counter to 0 raises ValueError."""
        id_manager = IDManager()

        with pytest.raises(ValueError, match="Counter must be a positive integer"):
            id_manager.set_counter(0)

    def test_set_counter_with_negative_raises_value_error(self):
        """Test that setting counter to negative value raises ValueError."""
        id_manager = IDManager()

        with pytest.raises(ValueError, match="Counter must be a positive integer"):
            id_manager.set_counter(-5)

    def test_set_counter_with_non_integer_raises_type_error(self):
        """Test that setting counter to non-integer raises TypeError."""
        id_manager = IDManager()

        with pytest.raises(TypeError, match="Counter must be an integer"):
            id_manager.set_counter("10")

        with pytest.raises(TypeError, match="Counter must be an integer"):
            id_manager.set_counter(10.5)

    def test_set_counter_after_generating_ids(self):
        """Test setting counter after generating some IDs."""
        id_manager = IDManager()

        # Generate some IDs
        id_manager.generate_id()  # 1
        id_manager.generate_id()  # 2

        # Set counter to higher value
        id_manager.set_counter(100)

        next_id = id_manager.generate_id()
        assert next_id == 100


class TestCounterReset:
    """Test ID counter reset after delete all."""

    def test_reset_counter_to_one(self):
        """Test resetting counter to 1."""
        id_manager = IDManager()

        # Generate some IDs
        id_manager.generate_id()  # 1
        id_manager.generate_id()  # 2
        id_manager.generate_id()  # 3

        # Reset counter
        id_manager.reset_counter()

        # Next ID should be 1
        next_id = id_manager.generate_id()
        assert next_id == 1

    def test_reset_counter_multiple_times(self):
        """Test resetting counter multiple times."""
        id_manager = IDManager()

        # First cycle
        id_manager.generate_id()  # 1
        id_manager.generate_id()  # 2
        id_manager.reset_counter()

        # Second cycle
        id_manager.generate_id()  # 1
        id_manager.generate_id()  # 2
        id_manager.reset_counter()

        # Third cycle
        next_id = id_manager.generate_id()
        assert next_id == 1

    def test_reset_counter_in_initial_state(self):
        """Test resetting counter when no IDs have been generated."""
        id_manager = IDManager()

        id_manager.reset_counter()

        next_id = id_manager.generate_id()
        assert next_id == 1

    def test_get_current_counter_after_reset(self):
        """Test getting counter value after reset."""
        id_manager = IDManager()

        # Generate some IDs
        id_manager.generate_id()
        id_manager.generate_id()

        # Reset
        id_manager.reset_counter()

        # Counter should be 1
        current = id_manager.get_current_counter()
        assert current == 1


class TestCounterPersistence:
    """Test ID counter persistence across instances."""

    def test_counter_state_can_be_saved_and_restored(self):
        """Test that counter state can be saved and restored."""
        # First instance
        id_manager1 = IDManager()
        id_manager1.generate_id()  # 1
        id_manager1.generate_id()  # 2
        id_manager1.generate_id()  # 3

        # Save counter state
        saved_counter = id_manager1.get_current_counter()
        assert saved_counter == 4

        # Second instance (simulating app restart)
        id_manager2 = IDManager()
        id_manager2.set_counter(saved_counter)

        # Should continue from where we left off
        next_id = id_manager2.generate_id()
        assert next_id == 4

    def test_multiple_instances_independent(self):
        """Test that multiple IDManager instances are independent."""
        id_manager1 = IDManager()
        id_manager2 = IDManager()

        id1 = id_manager1.generate_id()
        id2 = id_manager2.generate_id()

        # Both should start from 1 (independent counters)
        assert id1 == 1
        assert id2 == 1

        # Continue generating
        id_manager1.generate_id()  # 2
        id_manager1.generate_id()  # 3

        id_manager2.generate_id()  # 2

        # Verify independence
        assert id_manager1.get_current_counter() == 4
        assert id_manager2.get_current_counter() == 3


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_generate_many_ids(self):
        """Test generating a large number of IDs."""
        id_manager = IDManager()

        # Generate 1000 IDs
        ids = [id_manager.generate_id() for _ in range(1000)]

        # Verify all unique and sequential
        assert len(ids) == 1000
        assert len(set(ids)) == 1000  # All unique
        assert ids == list(range(1, 1001))

    def test_counter_after_set_and_reset(self):
        """Test counter behavior after set and reset operations."""
        id_manager = IDManager()

        # Set to high value
        id_manager.set_counter(100)
        assert id_manager.generate_id() == 100

        # Reset
        id_manager.reset_counter()
        assert id_manager.generate_id() == 1

        # Set again
        id_manager.set_counter(50)
        assert id_manager.generate_id() == 50


class TestDeleteAllScenario:
    """Test ID management in delete all scenario."""

    def test_delete_all_workflow(self):
        """Test complete delete all workflow with ID reset."""
        id_manager = IDManager()

        # Create some tasks
        task_ids = [id_manager.generate_id() for _ in range(5)]
        assert task_ids == [1, 2, 3, 4, 5]

        # Simulate delete all (reset counter)
        id_manager.reset_counter()

        # Create new tasks (should start from 1 again)
        new_task_ids = [id_manager.generate_id() for _ in range(3)]
        assert new_task_ids == [1, 2, 3]

    def test_counter_persistence_after_delete_all(self):
        """Test that counter persists correctly after delete all."""
        # Before delete all
        id_manager1 = IDManager()
        id_manager1.generate_id()  # 1
        id_manager1.generate_id()  # 2

        # Delete all and reset
        id_manager1.reset_counter()
        saved_counter = id_manager1.get_current_counter()
        assert saved_counter == 1

        # Simulate app restart
        id_manager2 = IDManager()
        id_manager2.set_counter(saved_counter)

        # Should start from 1
        next_id = id_manager2.generate_id()
        assert next_id == 1
