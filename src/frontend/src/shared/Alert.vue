<script setup lang="ts">
defineProps<{
  message?: string
  type?: 'success' | 'error' | 'warning' | 'info'
}>()

const emits = defineEmits<{
  close: []
}>()
</script>

<template>
  <div class="alert" :class="`alert-${type || 'info'}`">
    <span class="alert-message">{{ message }}</span>
    <button class="alert-close" @click="emits('close')" aria-label="關閉">
      ×
    </button>
  </div>
</template>

<style scoped>
.alert {
  padding: 12px 16px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert-warning {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
}

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.alert-message {
  flex: 1;
  font-size: 14px;
}

.alert-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: inherit;
  padding: 0;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.alert-close:hover {
  opacity: 1;
}
</style>
