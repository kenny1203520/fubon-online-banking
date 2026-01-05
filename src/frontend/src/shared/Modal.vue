<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  isOpen?: boolean
  size?: 'small' | 'medium' | 'large'
}

interface Emits {
  close: []
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: false,
  size: 'medium',
})

const emit = defineEmits<Emits>()

const isVisible = computed(() => props.isOpen)

const handleBackdropClick = () => {
  emit('close')
}
</script>

<template>
  <teleport to="body">
    <transition name="modal">
      <div v-if="isVisible" class="modal-backdrop" @click="handleBackdropClick">
        <div class="modal" :class="`modal-${size}` " @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">{{ title }}</h2>
            <button class="modal-close" @click="handleBackdropClick">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <div class="modal-content">
            <slot></slot>
          </div>
          <div class="modal-footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-small {
  width: 300px;
}

.modal-medium {
  width: 500px;
}

.modal-large {
  width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #333;
}

.modal-content {
  padding: 20px;
  flex: 1;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal {
  transform: scale(0.9);
}

.modal-leave-to .modal {
  transform: scale(0.9);
}

@media (max-width: 768px) {
  .modal-small,
  .modal-medium,
  .modal-large {
    width: calc(100% - 40px);
  }
}
</style>
