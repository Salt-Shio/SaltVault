<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useVfsStore } from '@/stores/vfs'
import LightningCursor from '@/components/ui/LightningCursor.vue'
import { Menu, X } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const vfsStore = useVfsStore()

// 使用 Pinia store 的真實登入狀態
const isLoggedIn = computed(() => authStore.isLoggedIn)

// 手機窄螢幕（< sm）導覽選單改用漢堡選單收合，避免中文字被擠到換行
const isMobileMenuOpen = ref(false)

watch(() => route.path, () => {
  isMobileMenuOpen.value = false
})

const logout = () => {
  authStore.logout()
  vfsStore.clearState()
  router.push('/')
}

// 根據路由名稱來決定要顯示的中文麵包屑
const currentRouteName = computed(() => {
  const nameMap: Record<string, string> = {
    'home': '主頁',
    'login': '登入',
    'register': '註冊',
    'explorer': '檔案系統',
    'settings': '設定',
  }
  return route.name && typeof route.name === 'string' ? (nameMap[route.name] || route.name) : ''
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-mono-900 text-mono-50 font-sans selection:bg-mono-500 selection:text-white">
    <LightningCursor />
    <!-- Navbar (科技終端機風格) -->
    <nav class="bg-black flex items-center justify-between px-4 md:px-8 py-3 md:py-5 border-b border-mono-700 relative z-20">
      <div class="flex items-center">
        <!-- Logo 結合 Monospace 與閃爍游標 -->
        <router-link to="/" class="text-2xl lg:text-4xl font-mono font-bold hover:text-white transition-all duration-300 flex items-center group">
          <span class="text-mono-500 mr-2 lg:mr-4 font-normal group-hover:text-mono-400">&gt;</span>
          <span class="text-mono-200 tracking-wider uppercase group-hover:text-white group-hover:[text-shadow:0_0_15px_rgba(255,255,255,0.4)]">Salt_Vault</span>
          <span class="animate-terminal-blink ml-1 font-normal">_</span>
        </router-link>
      </div>

      <!-- 桌面版 inline 選單（sm 以上顯示） -->
      <div class="hidden sm:flex gap-4 lg:gap-10 items-center font-mono text-base lg:text-2xl tracking-widest">
        <!-- 未登入狀態 -->
        <template v-if="!isLoggedIn">
          <router-link
            to="/register"
            class="text-mono-400 hover:text-white transition-all duration-200 flex items-center gap-2 group"
          >
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">[</span>
            註冊
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">]</span>
          </router-link>
          <router-link
            to="/login"
            class="text-mono-400 hover:text-white transition-all duration-200 flex items-center gap-2 group"
          >
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">[</span>
            登入
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">]</span>
          </router-link>
        </template>

        <!-- 已登入狀態 -->
        <template v-else>
          <router-link
            to="/explore"
            class="text-mono-400 hover:text-white transition-all duration-200 flex items-center gap-2 group"
          >
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">[</span>
            檔案系統
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">]</span>
          </router-link>
          <router-link
            to="/config"
            class="text-mono-400 hover:text-white transition-all duration-200 flex items-center gap-2 group"
          >
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">[</span>
            設定
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">]</span>
          </router-link>
          <button
            @click="logout"
            class="text-mono-400 hover:text-white transition-all duration-200 flex items-center gap-2 group cursor-pointer"
          >
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">[</span>
            登出
            <span class="text-mono-700 group-hover:text-mono-400 transition-colors">]</span>
          </button>
        </template>
      </div>

      <!-- 手機版漢堡按鈕（sm 以下顯示） -->
      <button
        @click="isMobileMenuOpen = !isMobileMenuOpen"
        class="sm:hidden text-mono-200 hover:text-white p-2 -mr-2 cursor-pointer"
      >
        <X v-if="isMobileMenuOpen" class="w-6 h-6" />
        <Menu v-else class="w-6 h-6" />
      </button>

      <!-- 手機版下拉選單 -->
      <div
        v-if="isMobileMenuOpen"
        class="sm:hidden absolute top-full left-0 w-full bg-black border-b border-mono-700 flex flex-col font-mono text-lg tracking-widest z-30 shadow-lg"
      >
        <template v-if="!isLoggedIn">
          <router-link to="/register" class="px-4 py-4 border-b border-mono-800 text-mono-300 hover:text-white hover:bg-mono-900 transition-colors">
            [ 註冊 ]
          </router-link>
          <router-link to="/login" class="px-4 py-4 text-mono-300 hover:text-white hover:bg-mono-900 transition-colors">
            [ 登入 ]
          </router-link>
        </template>
        <template v-else>
          <router-link to="/explore" class="px-4 py-4 border-b border-mono-800 text-mono-300 hover:text-white hover:bg-mono-900 transition-colors">
            [ 檔案系統 ]
          </router-link>
          <router-link to="/config" class="px-4 py-4 border-b border-mono-800 text-mono-300 hover:text-white hover:bg-mono-900 transition-colors">
            [ 設定 ]
          </router-link>
          <button @click="logout" class="px-4 py-4 text-left text-mono-300 hover:text-white hover:bg-mono-900 transition-colors cursor-pointer">
            [ 登出 ]
          </button>
        </template>
      </div>
    </nav>

    <!-- 麵包屑導航 (Phase 5.2 需求) -->
    <div v-if="route.path !== '/' && currentRouteName" class="bg-mono-900 border-b border-mono-800 px-4 md:px-10 py-2 md:py-3 flex items-center gap-4 relative overflow-hidden z-10">
      <!-- 背景科幻網格點綴 -->
      <div class="absolute inset-0 opacity-[0.04] pointer-events-none" style="background-image: radial-gradient(#fff 1px, transparent 1px); background-size: 20px 20px;"></div>

      <p class="font-mono text-base md:text-xl tracking-widest text-mono-400 flex items-center z-10">
        <router-link to="/" class="hover:text-white transition-colors">主頁</router-link>
        <span class="mx-2 md:mx-4 text-mono-600 font-normal">/</span>
        <span class="text-mono-100 font-bold">
          {{ currentRouteName }}
        </span>
      </p>
    </div>

    <!-- 頁面主體 -->
    <main class="flex-grow bg-mono-900 relative">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes terminal-blink {
  0%, 100% { 
    opacity: 1; 
    color: #fff;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
  }
  50% { 
    opacity: 0; 
  }
}

.animate-terminal-blink {
  animation: terminal-blink 1s step-end infinite;
}
</style>
