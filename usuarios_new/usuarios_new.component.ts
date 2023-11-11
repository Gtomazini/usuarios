
import { User } from '../usuarios.model';
import { UsuariosService } from '../usuarios.service';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { LoginService } from '../../auth/login.service';
import { MessageService } from 'primeng/api';
import { MenuItem } from 'primeng/api';



@Component({
    selector: 'app-usuarios-create',
    templateUrl: './usuarios_new.component.html',
    styleUrls: ['./usuarios_new.component.css'],
    providers: [MessageService]
})

export class UsuariosNewComponent implements OnInit {
    
    //Breadcrumb
    items: MenuItem[] | undefined;
    home: MenuItem | undefined;

    //Objeto principal do form
    usuario: User = {
        primeiro_nome : "",
        sobrenome : "",
        username : "",
        email : "",
        usuario_id: null,
        ativo : null
    }
        
    constructor(private loginService: LoginService, private usuariosService: UsuariosService, private router: Router, public messageService: MessageService,) {
        setTimeout(() => {
            this.loginService.validateSession()
             if (!this.loginService.sessionIsValid){
                this.messageService.add({ severity: 'error', summary: 'Sessão encerrada', detail: 'Deslogado por inatividade' });
                this.router.navigate(['/auth/login'])
            }
        }, 500)		
    }

    ngOnInit(): void {
        // Componente Breadcrumb
        this.items = [{ label: 'Usuário', routerLink: '/app/usuarios' }, { label: 'Novo Registro' }];
        this.home = { icon: 'pi pi-home', routerLink: '/app/dashboard' };
    }
    
    create(): void {

        this.usuario.primeiro_nome = this.usuario.primeiro_nome.toUpperCase().trim()
        this.usuario.sobrenome = this.usuario.sobrenome.toUpperCase().trim()
        this.usuario.email = this.usuario.email.toUpperCase().trim()

        this.usuariosService.create(this.usuario).subscribe({
            next: () => {
                this.messageService.add({key: 'tst', severity: 'success', summary: 'SUCESSO', detail: 'Registro gravado com sucesso!' });
                setTimeout(() => {
                    this.router.navigate(['/app/usuarios'])
                }, 2500)                                
            },
            complete: () => {},
            error: (e) => { 
                if (e.error['message err'] !== undefined) {
                    this.messageService.add({key: 'tst', severity: 'error', summary: 'ATENÇÃO', detail: e.error['message err'] });
                } else {
                    this.messageService.add({key: 'tst', severity: 'error', summary: 'ATENÇÃO', detail: 'Não foi possível executar a ação.' });
                }
                
            }	
        })
    }
    
    cancel(): void {       
        this.router.navigate(['/app/usuarios'])
    }
    

}