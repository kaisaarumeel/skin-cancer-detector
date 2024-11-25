<script lang="ts">
    import { goto } from '$app/navigation';
    import UserList from '../../components/UserList.svelte';
    import AdminUpload from '../../components/AdminUpload.svelte';
    import ModelVersions from '../../components/ModelVersions.svelte';
    import ModelAccuracy from '../../components/ModelAccuracy.svelte';
    import Retrain from '../../components/Retrain.svelte';

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
  
    <div class="p-6 flex flex-row gap-2 flex-wrap">
      <div class="gap-6">
        <div>
          <AdminUpload></AdminUpload>

        </div>
        <div class="mt-2">
          <Retrain></Retrain>

        </div>
      </div>
      <div class="h-fit grow">
        <div class="w-full">
          <ModelVersions></ModelVersions>

        </div>
        <div class="mt-2">
          <ModelAccuracy></ModelAccuracy>

        </div>

      </div>

    </div>
    <UserList></UserList>

  </div>
  