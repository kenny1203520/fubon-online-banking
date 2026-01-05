<script setup lang="ts">
</script>

<template>
  <main>
    <section>
      <h1>帳戶管理示範</h1>
      <p>選擇下面功能以進入對應示範頁面：</p>
      <ul>
        <li><router-link to="/accounts">帳戶管理</router-link></li>
        <li><router-link to="/transactions">交易功能</router-link></li>
        <li><router-link to="/investments">投資理財</router-link></li>
        <li><router-link to="/creditcards">信用卡</router-link></li>
        <li><router-link to="/loans">貸款</router-link></li>
      </ul>
    </section>
  </main>
</template>
