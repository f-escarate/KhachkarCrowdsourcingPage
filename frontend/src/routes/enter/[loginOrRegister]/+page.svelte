<script>
    import { Tabs, TabItem, FloatingLabelInput , Button, Spinner} from 'flowbite-svelte';
    import { base } from "$app/paths";
    import { goto } from "$app/navigation";
    import Cookies from 'js-cookie';
    import { HOST } from '$lib/constants';

    /** @type {import('./$types').PageData} */
	export let data;
    $: loginOrRegister = data.loginOrRegister;
    
    let name = '';
    let email = '';
    let pass = '';
    let pass2 = '';
    let isLoading = false;

    const handleLogin = async () => {
        isLoading = true;
        const data = new FormData();
        data.append('username', email);
        data.append('password', pass);
        const response = await fetch(`${HOST}/token`, {
            method: "POST",
            body: data
        });
        const json = await response.json();
        if (json.status == 'success') {
            Cookies.set('token', json.access_token, { sameSite:'strict', secure:true });
            alert('Successfully logged in, redirecting to home page');
            window.location.href = base;
            return;
        }
        alert('Username or password incorrect');
        isLoading = false;
    }

    const handleRegister = async () => {
        if (pass != pass2) {
            alert('Passwords do not match');
            return;
        }
        isLoading = true;
        const data = new FormData();
        data.append('username', name);
        data.append('email', email);
        data.append('password', pass);
        data.append('password2', pass2);
        const response = await fetch(`${HOST}/register/`, {
            method: "POST",
            body: data
        });
        const json = await response.json();
        if (json.status == 'success') {
            alert('Successfully registered, you can now log in');
            goto(`${base}/enter/login`);
        }
        else if (json.status == 'error') {
            alert(json.msg);
        }
        isLoading = false;
    }
    const onEnter = (e, func) => {
        if (e.key == 'Enter') {
            func();
        }
    }


</script>

<div class='md:mx-auto md:max-w-[50%] my-5 h-full md:p-4 space-y-4'>
    <Tabs style="underline">
        <TabItem open={loginOrRegister==='login'} on:click={e=> goto(`${base}/enter/login`)}>
            <span slot="title">Log In</span>
            <div class='flex flex-col gap-4'>
                <FloatingLabelInput style="filled" bind:value={email} on:keydown={(e)=>onEnter(e, handleLogin)} name="email" id="email" type="text" label="Email"/>
                <FloatingLabelInput style="filled" bind:value={pass}  on:keydown={(e)=>onEnter(e, handleLogin)} name="password" id="password" type="password" label="Password"/>
                {#if isLoading}
                    <Button class="bg-amber-500 text-black" size="sm" disabled>
                        <Spinner class="mr-2" size="4"/>
                        Logging In
                    </Button>
                {:else}
                    <Button class="bg-amber-500 text-black" size="sm" on:click={handleLogin}>Log In</Button>
                {/if}
            </div>
        </TabItem>
        <TabItem open={loginOrRegister==='register'} on:click={e=> goto(`${base}/enter/register`)}>
            <span slot="title">Register</span>
            <div class='flex flex-col gap-4'>
                <FloatingLabelInput bind:value={name}  on:keydown={(e)=>onEnter(e, handleRegister)} style="filled" name="name" id="name" type="text" label="Name"/>
                <FloatingLabelInput bind:value={email} on:keydown={(e)=>onEnter(e, handleRegister)} style="filled" name="email" id="register_email" type="text" label="Email"/>
                <FloatingLabelInput bind:value={pass}  on:keydown={(e)=>onEnter(e, handleRegister)} style="filled" name="password" id="register_password" type="password" label="Password"/>
                <FloatingLabelInput bind:value={pass2} on:keydown={(e)=>onEnter(e, handleRegister)} style="filled" name="password2" id="register_password2" type="password" label="Repeat your password"/>
                {#if isLoading}
                    <Button class="bg-amber-500 text-black" size="sm" disabled>
                        <Spinner class="mr-2" size="4"/>
                        Registering
                    </Button>
                {:else}
                    <Button class="bg-amber-500 text-black" size="sm" on:click={handleRegister}>Register</Button>
                {/if}
            </div>
        </TabItem>
    </Tabs>    
</div>
  