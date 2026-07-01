<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <div class="text-center p-4">
    <button
      class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
      @click="count++"
    >
      点击次数: {{ count }}
    </button>
  </div>
</template>