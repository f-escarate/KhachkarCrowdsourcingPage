<script>
    import { Avatar, Dropdown, DropdownHeader, DropdownItem, DropdownDivider, NavHamburger, Button } from 'flowbite-svelte';
    import UserIcon from './icons/UserIcon.svelte';
    import Cookies from 'js-cookie';
    import { onMount } from 'svelte';
    import { HOST } from '$lib/constants';
    import { base } from "$app/paths";
    export let authenticated;

    let data = {
        name: '',
        email: '',
        image: '',
        is_admin: false,
    };
    onMount(async () => {
        if(Cookies.get('token') === undefined) return;
        const response = 
            await fetch(`${HOST}/me/`, {
                method: "GET",
                headers: {
                    accept: "application/json",
                    Authorization: `Bearer ${Cookies.get('token')}`
                }
            });
        const json = await response.json();
        if (json.status == 'success') {
            data.name = json.username;
            data.email = json.email;
            data.image = '';
            data.is_admin = json.is_admin;
            authenticated = true;
        } else {
            authenticated = false;
            Cookies.remove('token');
        }
    });
    const handleLogOut = () => {
        Cookies.remove('token');
        data.authenticated = false;
        window.location.href = base;
    }

</script>

{#if authenticated}
    <div class="flex items-center md:order-2">
        <Avatar id="avatar-menu" src={data.image} />
        <NavHamburger class1="w-full md:flex md:w-auto md:order-1" />
    </div>
    <Dropdown placement="bottom" triggeredBy="#avatar-menu">
        <DropdownHeader>
            <span class="block text-sm">{data.name}</span>
            <span class="block truncate text-sm font-medium">{data.email}</span>
        </DropdownHeader>
        <DropdownItem href={`${base}/myKhachkars/`}>My Khachkars</DropdownItem>
        <DropdownItem href={`${base}/account/`}>Account Settings</DropdownItem>
        {#if data.is_admin}
            <DropdownItem href={`${base}/compileAssetBundles/`}>Compile Asset Bundles</DropdownItem>
        {/if}
        <DropdownDivider />
        <DropdownItem on:click={handleLogOut}>Log out</DropdownItem>
    </Dropdown>
{:else}
    <div class="flex md:order-2 gap-2">
        <Button size="sm" href={`${base}/login`} class="bg-amber-500 text-black">
            <UserIcon sx='m-0 text-black'/>
            Log In
        </Button>
        <NavHamburger class1="w-full md:flex md:w-auto md:order-1" />
    </div>
{/if}