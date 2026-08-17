Hey, I just ran a quick security audit on our credential vault and it's a mess. A bunch of passwords are way too weak for their category. I've dumped the vault contents into `vault/` and the password policies are in `policies/`. 

Can you go through every credential in `vault/`, check its category against the right policy, and then write a list of all the weak ones into `ops/weak_creds.json`? Each entry should have the credential ID and a brief reason why it's weak. I need this ASAP so we can rotate those credentials.

Oh, and watch out – one of the files in `vault/` might be corrupted, but just skip it if you can't parse it. Don't waste time on it.

Let me know once it's done.
