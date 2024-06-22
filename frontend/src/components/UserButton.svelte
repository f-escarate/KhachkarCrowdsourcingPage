<script>
    import { Avatar, Dropdown, DropdownHeader, DropdownItem, DropdownDivider, NavHamburger, Button } from 'flowbite-svelte';
    import UserIcon from './icons/UserIcon.svelte';
    import UserAddIcon from './icons/UserAddIcon.svelte';
    import { auth_get_json } from '$lib/utils';
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
        if(Cookies.get('access_token') === undefined) return;
        const response = await auth_get_json(`${HOST}/me/`);
        const json = await response.json();
        if (json.status == 'success') {
            data.name = json.username;
            data.email = json.email;
            data.image = '';
            data.is_admin = json.is_admin;
            authenticated = true;
        } else {
            authenticated = false;
            Cookies.remove('access_token');
        }
    });
    const handleLogOut = () => {
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        data.authenticated = false;
        window.location.href = base;
    }

</script>

{#if authenticated}
    <div class="flex items-center md:order-2">
        <Avatar id="avatar-menu" src={data.image} />
        <NavHamburger />
    </div>
    <Dropdown placement="bottom" triggeredBy="#avatar-menu">
        <DropdownHeader>
            <span class="block text-sm">{data.name}</span>
            <span class="block truncate text-sm font-medium">{data.email}</span>
        </DropdownHeader>
        <DropdownItem href={`${base}/account/`}>Account Settings</DropdownItem>
        {#if data.is_admin}
            <DropdownItem href={`${base}/compileAssetBundles/`}>Compile Asset Bundles</DropdownItem>
        {/if}
        <DropdownDivider />
        <DropdownItem on:click={handleLogOut}>Log out</DropdownItem>
    </Dropdown>
{:else}
    <div class="md:order-2">
        <div class='hidden md:block'>
            <Button size="sm" href={`${base}/enter/login`} class="pl-1 pr-2 bg-amber-500 hover:bg-amber-600 text-black relative">
                <UserIcon sx='m-0 text-black'/>
                Log In
            </Button>
            <Button size="sm" href={`${base}/enter/register`} class="pl-1 pr-2 border-2 border-black bg-amber-100 hover:bg-amber-400 text-black relative">
                <UserAddIcon sx='m-0 text-black'/>
                Register
            </Button>
        </div>
        <NavHamburger/>
    </div>
{/if}