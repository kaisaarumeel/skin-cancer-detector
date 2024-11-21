<script lang="ts">
    import { goto } from '$app/navigation';
    import UserList from '../../components/UserList.svelte';
    import AdminUpload from '../../components/AdminUpload.svelte';
    import ModelVersions from '../../components/ModelVersions.svelte';
    import ModelAccuracy from '../../components/ModelAccuracy.svelte';

    function handleLogout() {
      // Add logout endpoint/logic here later
      goto('/home');
    }
  
  </script>
  
  <div class="h-screen flex flex-col">
    <header class="bg-primary shadow h-16 p-4 flex justify-between">
      <h1 class="text-xl font-extralight text-white">Admin Dashboard</h1>
      <button class="pr-20 font-light text-white" on:click={handleLogout}>Log out</button>
    </header>
  
    <div class="p-6 flex-1 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <AdminUpload></AdminUpload>
      <UserList></UserList>
      <ModelVersions></ModelVersions>
      <ModelAccuracy></ModelAccuracy>
    </div>
  </div>
  