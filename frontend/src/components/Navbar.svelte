<script>
    import { Navbar, NavBrand, NavLi, NavUl, Button, NavHamburger } from 'flowbite-svelte';
    import UserIcon from './icons/UserIcon.svelte';
    import UserAddIcon from './icons/UserAddIcon.svelte';
    import { base } from "$app/paths";
    var nonActiveClass = 'text-xl md:transition-all md:hover:text-amber-400 md:hover:scale-125'
    var activeClass = nonActiveClass+' md:border-amber-400 md:border-b-2 md:rounded-none'

    import { page } from '$app/stores';
    import UserButton from './UserButton.svelte';
    $: activeUrl = $page.url.pathname;
    let authenticated;
</script>

<Navbar class="md:px-10">
    <NavBrand href={base}>
        <img src={`${base}/favicon.ico`} class="me-3 h-6 sm:h-9" alt="Logo" />
        <span class="self-center whitespace-nowrap text-2xl font-semibold dark:text-white">UpKhachkar</span>
    </NavBrand>
    <UserButton bind:authenticated/>
    <NavUl {activeUrl} {activeClass} {nonActiveClass}>
        <NavLi href={base}>Home</NavLi>
        {#if authenticated}
            <NavLi href={`${base}/add/`}>Add Khachkar</NavLi>
        {/if}
        <NavLi href={`${base}/viewKhachkars/`}>View Khachkars</NavLi>
        <NavLi href={`${base}/tutorial/`}>Tutorial</NavLi>
        <div class='md:hidden md:m-0 md:w-0 md:p-0'>
            <NavLi class='flex items-center gap-1 bg-amber-400 md:mb-1' href={`${base}/enter/login`}>
                <UserIcon sx='m-0 text-black'/>
                Log in
            </NavLi>
            <NavLi class='flex items-center gap-1 bg-amber-300' href={`${base}/enter/register`}>
                <UserAddIcon sx='m-0 text-black'/>
                Register
            </NavLi>
        </div>
        
    </NavUl>
</Navbar>