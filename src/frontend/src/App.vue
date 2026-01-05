<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import Header from '@/layouts/Header.vue'
import Sidebar from '@/layouts/Sidebar.vue'
import Footer from '@/layouts/Footer.vue'

const route = useRoute()

// 判斷是否是需要布局的頁面
const isAuthPage = computed(() => {
    return route.path.startsWith('/login') || route.path.startsWith('/register')
})

const isFullWidthPage = computed(() => {
    return isAuthPage.value
})
</script>

<template>
    <div id="app" class="app-container">
        <!-- 認證頁面不顯示導航列 -->
        <template v-if="isFullWidthPage">
            <RouterView />
        </template>

        <!-- 主頁面 -->
        <template v-else>
            <Header></Header>
            <Sidebar />
            <main class="content">
                <RouterView />
            </main>
            <Footer></Footer>
        </template>
    </div>
</template>

<style scoped>
.app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: #f5f5f5;
}

.content {
    flex: 1;
    margin-top: 120px; /* header 60px + sidebar 60px */
    padding: 20px;
    overflow-y: auto;
    min-height: calc(100vh - 120px);
}

@media (max-width: 768px) {
    .content {
        margin-top: 110px; /* header 50px + sidebar 60px */
        padding: 16px;
    }
}
</style>
