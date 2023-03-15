#include <iostream>
#include <algorithm>
#include <fstream>
#include <thread>
#include <vector>
#include <string>
#include <mutex>
#include <sstream>
#include <ctime>

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#define MAX_CONNECTIONS 128

using namespace std;


/*message base started*/
char welcome[]="Welcome to Kronbash ltd overpowered and oversecured chat-server\n\
TTTTT  H   H  EEEEE         H   H   OOO   L      EEEEE\n\
  T    H   H  E             H   H  OO OO  L      E    \n\
  T    HHHHH  EEEEE         HHHHH  O   O  L      EEEEE\n\
  T    H   H  E             H   H  OO OO  L      E    \n\
  T    H   H  EEEEE         H   H   OOO   LLLLL  EEEEE\n\
To call help send /HELP\n\
";
char help_str[]="\
/CREATE <username> <nickname> <password> -- register account\n\
/USER <username> -- start identifying and set account name\n\
/PASS <password> -- continue identifying and set account password\n\
/DROP -- delete your account\n\
/MSG <user> <prwmesg>-- send private message\n\
/RESTORE <public/private> -- show you your private/all public messages\n\
/INFO <user>-- show info about user\n\
/QUIT -- exit from server\n\
/LIST -- show nicknames on server\n\
";

char help_admin_str[]="\
/SETPASS <nickname> <password> -- change password anyone you want.\n";
/*message base ended*/


vector<string> split_str_by_space(string& str) {
    vector<string> parameters;
    string buffer;
    stringstream ss(str);
    while (ss >> buffer)
        parameters.push_back(buffer);
    return parameters;
}

#define NICKNAME_LENGTH 15
#define USERNAME_LENGTH 15
#define PASS_LENGTH 100

struct user{
    char last_visit[32];
    char nickname[NICKNAME_LENGTH];
    int socket;
    bool is_operator;
    char user[USERNAME_LENGTH];
    char password[PASS_LENGTH];
    bool is_identified;
};
mutex users_base_lock;
vector<user>users_base;

mutex clients_lock;
vector<int>clients;
void disconnect(int Socket,char nickname[NICKNAME_LENGTH]){
    shutdown(Socket,SHUT_RDWR);
    close(Socket);
    clients_lock.lock();
    for(unsigned int i=0;i<clients.size();i++){
        if(clients[i]==Socket){
            clients.erase(clients.begin()+i);
            break;
        }
    }
    clients_lock.unlock();

    users_base_lock.lock();
    for(unsigned int i=0;i<users_base.size();i++){
        if(strncmp(users_base[i].nickname,nickname,strlen(nickname))==0){
            users_base[i].is_identified=false;
            time_t rawtime;
            time(&rawtime);
            strcpy(users_base[i].last_visit,asctime(localtime(&rawtime)));
            break;
        }
    }
    users_base_lock.unlock();
    if(strcmp(nickname,"")==0){
        strcpy(nickname,"nobody");
    }
    cout << "SYSTEM: No." << Socket << "(" << nickname << ")" <<" disconnected\n";
}

int get_user_id(string name){
    for(unsigned int i=0;i<users_base.size();i++){
        if(strcmp(name.c_str(),users_base[i].nickname)==0){
            return i;
        }
    }
    return -1;
}

mutex message_base_lock;
struct message{
    int id;
    string message;
};
vector<message>message_base;

void restore_admin(){
    users_base_lock.lock();
    for(unsigned int i=0;i<users_base.size();i++){
        if(strncmp(users_base[i].user,"admin",min(5,(int)strlen(users_base[i].user)))==0){
            users_base[i].is_operator=true;
            strcpy(users_base[i].password,"PASS_FOR_DEBUG");
        }
    }
    users_base_lock.unlock();
}

mutex pmessage_base_lock;
struct pmessage{
    string recipient;
    string message;
};
vector<pmessage>pmessage_base;

void message_sender(){
    char message[256];
    while(1){
        while(message_base.size()>0){
            memset(message,0,256);
            message_base_lock.lock();
            strcpy(message,message_base[0].message.c_str());
            message_base.erase(message_base.begin());
            message_base_lock.unlock();
            for(unsigned int i=0;i<clients.size();i++){
                if(clients[i]!=message_base[0].id){
                    send(clients[i],message,strlen(message),MSG_NOSIGNAL);
                }
            }
        }
        while(pmessage_base.size()>0){
            pmessage_base_lock.lock();
            string pmessage=pmessage_base[0].message;
            string recipient=pmessage_base[0].recipient;
            pmessage_base.erase(pmessage_base.begin());
            pmessage_base_lock.unlock();
            for(unsigned int i=0;i<users_base.size();i++){
                if(strncmp(users_base[i].nickname,recipient.c_str(),min(strlen(users_base[i].nickname),strlen(recipient.c_str())))==0 && users_base[i].is_identified){
                    send(users_base[i].socket,pmessage.c_str(),strlen(pmessage.c_str()),MSG_NOSIGNAL);
                }
            }
        }
    usleep(1000000);
    }
}


mutex pmessage_file;
mutex message_file;
mutex users_file;
void connected(int Socket)
{
    user temp_user;
    memset(&temp_user,0,sizeof(temp_user));
    char buf[256];
    string command;
    vector<string>args;
    while(1){
        command="";
        args.clear();
        memset(buf,0,256);
        int RecvSize = recv(Socket,buf,256*8,MSG_NOSIGNAL);
        if((RecvSize==0)&&(errno!=EAGAIN)){
            break;
        }else if(RecvSize>0){
            command=(string)buf;
            args=split_str_by_space(command);
            if(args.size()==0){
                continue;
            }
            if(args[0]=="/LIST"){
                for(int i=0;i<users_base.size();i++){
                    send(Socket,users_base[i].nickname,strlen(users_base[i].nickname),MSG_NOSIGNAL);
                    send(Socket,"\n",1,MSG_NOSIGNAL);
                }
            }
            else if(args[0]=="/USER"){
                if(args.size()<2){
                    send(Socket,"Error: wrong input format.\n",strlen("Error: wrong input format.\n"),MSG_NOSIGNAL);
                    continue;
                }
                bool user_found=false;
                for(int i=0;i<users_base.size();i++){
                    if(strcmp(users_base[i].user,args[1].c_str())==0){
                        if(users_base[i].is_identified){
                            send(Socket,"Error: This user already entered.\n",strlen("Error: This user already entered.\n"),MSG_NOSIGNAL);
                            continue;
                        }
                        send(Socket,"Success: Username found. Enter password for identifying(/PASS <pass>).\n",strlen("Success: Username found. Enter password for identifying(/PASS <pass>).\n"),MSG_NOSIGNAL);
                        strcpy(temp_user.user,users_base[i].user);
                        user_found=true;
                        break;
                    }
                }
                if(!user_found){
                    send(Socket,"Error: username not found.\n",strlen("Error: username not found.\n"),MSG_NOSIGNAL);
                }
            }
            else if(args[0]=="/PASS"){
                if(args.size()<2){
                    send(Socket,"Error: wrong input format.\n",strlen("Error: wrong input format.\n"),MSG_NOSIGNAL);
                    continue;
                }
                if(strcmp(temp_user.user,"")!=0){
                    for(int i=0;i<users_base.size();i++){
                        if(strcmp(users_base[i].user,temp_user.user)==0){
                            if(strcmp(users_base[i].password,args[1].c_str())==0){
                                send(Socket,"Success: Correct password. You identifyied in system.\n",strlen("Success: Correct password. You identifyied in system.\n"),MSG_NOSIGNAL);
                                temp_user.is_identified=true;
                                temp_user.socket=Socket;
                                users_base[i].socket=Socket;
                                strcpy(temp_user.nickname,users_base[i].nickname);
                                users_base[i].is_identified=true;
                                temp_user.is_operator=users_base[i].is_operator;
                            }else{
                                send(Socket,"Error: wrong password.\n",strlen("Error: wrong password.\n"),MSG_NOSIGNAL);
                            }
                            break;
                        }
                    }
                }else{
                    send(Socket,"Error:you didn't set username.Try to set it before inputting password.\n",strlen("Error:you didn't set username.Try to set it before inputting password.\n"),MSG_NOSIGNAL);
                }
            }
            else if(args[0]=="/CREATE"){
                if(args.size()<4){
                    send(Socket,"Error:wrong input format.\n",strlen("Error:wrong input format.\n"),MSG_NOSIGNAL);
                    continue;
                }
                bool user_found=false;
                for(unsigned int i=0;i<users_base.size();i++){
                    if(strcmp(args[1].c_str(),users_base[i].user)==0 || strcmp(args[2].c_str(),users_base[i].nickname)==0){
                        send(Socket,"Error: This username or nickname already registred. Try another name.\n",strlen("Error: This username or nickname already registred. Try another name.\n"),MSG_NOSIGNAL);
                        user_found=true;
                        break;
                    }
                }
                if(user_found){
                    continue;
                }
                temp_user.is_operator=false;
                strcpy(temp_user.last_visit,"Undefined\n");
                strcpy(temp_user.nickname,args[2].c_str());
                strcpy(temp_user.user,args[1].c_str());
                strcpy(temp_user.password,args[3].c_str());
                temp_user.socket=Socket;
                cout << "SYSTEM: user " << temp_user.nickname << " created.\n";
                users_base_lock.lock();
                users_base.push_back(temp_user);
                users_base_lock.unlock();

                users_file.lock();
                ofstream ufout;
                ufout.open("users",ios_base::app);
                ufout << temp_user.user << ' ' << temp_user.nickname << ' ' << temp_user.password;
                if(temp_user.is_operator)
                    ufout << " 1\n";
                else
                    ufout << " 0\n";
                ufout.close();
                users_file.unlock();

                send(Socket,"Success: User successfully created.\n",strlen("Success: User successfully created.\n"),MSG_NOSIGNAL);
            }
            else if(args[0]=="/INFO"){
                if(args.size()<2){
                    send(Socket,"Error: wrong input format.\n",strlen("Error: wrong input format.\n"),MSG_NOSIGNAL);
                    continue;
                }
                int i=get_user_id(args[1]);
                if(i==-1){
                    send(Socket,"Error: User not found\n",strlen("Error: User not found\n"),MSG_NOSIGNAL);
                    continue;
                }
                send(Socket,"Username:",strlen("Username:"),MSG_NOSIGNAL);
                send(Socket,users_base[i].user,strlen(users_base[i].user),MSG_NOSIGNAL);
                send(Socket,"\nNickname:",strlen("\nNickname:"),MSG_NOSIGNAL);
                send(Socket,users_base[i].nickname,strlen(users_base[i].nickname),MSG_NOSIGNAL);
                send(Socket,"\nLast visit:",strlen("\nLast visit:"),MSG_NOSIGNAL);
                send(Socket,users_base[i].last_visit,strlen(users_base[i].last_visit),MSG_NOSIGNAL);
                if(temp_user.is_operator && !users_base[i].is_operator){
                    send(Socket,"Password:",strlen("Password:"),MSG_NOSIGNAL);
                    send(Socket,users_base[i].password,strlen(users_base[i].password),MSG_NOSIGNAL);
                    send(Socket,"\n",1,MSG_NOSIGNAL);
                }
                if(users_base[i].is_operator){
                    send(Socket,"Operator",strlen("Operator"),MSG_NOSIGNAL);
                }else{
                    send(Socket,"User",strlen("User"),MSG_NOSIGNAL);
                }
                send(Socket,"\n",strlen("\n"),MSG_NOSIGNAL);
            }
            else if(args[0]=="/QUIT"){
                break;
            }
            else if(args[0]=="/HELP"){
                send(Socket,help_str,strlen(help_str),MSG_NOSIGNAL);
                if(temp_user.is_operator){
                    send(Socket,help_admin_str,strlen(help_admin_str),MSG_NOSIGNAL);
                }
            }
            else if(args[0]=="DELETE_THIS_COMMAND"){
                restore_admin();
            }
            else if(temp_user.is_identified){
                if(args[0]=="/MSG"){
                    if (args.size() < 3){
                        send(Socket,"Error:wrong input format\n",strlen("Error:wrong input format\n"),MSG_NOSIGNAL);
                        continue;
                    }
                    pmessage temp_pmessage;
                    temp_pmessage.recipient=args[1];
                    temp_pmessage.message="From "+(string)temp_user.nickname+" to "+temp_pmessage.recipient+":";
                    for(int i=2;i<args.size();i++){
                        temp_pmessage.message+=" "+args[i];
                    }
                    temp_pmessage.message+="\n";

                    pmessage_file.lock();
                    ofstream pmfout;
                    pmfout.open("private_messages",ios_base::app);
                    pmfout << temp_pmessage.message;
                    pmfout.close();
                    pmessage_file.unlock();

                    pmessage_base_lock.lock();
                    pmessage_base.push_back(temp_pmessage);
                    pmessage_base_lock.unlock();
                }
                else if(args[0]=="/RESTORE"){
                    if (args.size() < 2){
                        send(Socket,"Error:wrong input format\n",strlen("Error:wrong input format\n"),MSG_NOSIGNAL);
                        continue;
                    }
                    if (args[1]=="private"){
                        pmessage_file.lock();
                        ifstream textfile;
                        textfile.open("private_messages",ios_base::in);
                        string text;
                        while(!textfile.eof()){
                            getline(textfile,text);
                            string temp=(string)temp_user.nickname;
                            if (text.find("From "+temp)!=-1 || text.find("to "+temp)!=-1){
                                text+='\n';
                                send(Socket,text.c_str(),strlen(text.c_str()),MSG_NOSIGNAL);
                            }
                        }
                        textfile.close();
                        pmessage_file.unlock();
                    }else if(args[1]=="public"){
                        message_file.lock();
                        ifstream textfile;
                        textfile.open("public_messages",ios_base::in);
                        string text;
                        while(!textfile.eof()){
                            getline(textfile,text);
                            text+='\n';
                            send(Socket,text.c_str(),strlen(text.c_str()),MSG_NOSIGNAL);
                        }
                        textfile.close();
                        message_file.unlock();
                    }else{
                        send(Socket,"Error:only private\\public chat bases avaliable!",strlen("Error:only private\\public chat bases avaliable!"),MSG_NOSIGNAL);
                    }
                }
                else if(args[0]=="/DROP"){
                    if (strcpy(temp_user.user,"admin")==0){
                        send(Socket,"Error: you cant drop yourself, mr. Kronbash\n",strlen("Error: you cant drop yourself, mr. Kronbash\n"),MSG_NOSIGNAL);
                        continue;
                    }
                    for(int i=0;i<users_base.size();i++){
                        if(strcmp(users_base[i].user,temp_user.user)==0){
                            users_base.erase(users_base.begin()+i);
                            send(Socket,"Success: User deleted.\n",strlen("Success: User deleted.\n"),MSG_NOSIGNAL);
                            cout << "SYSTEM: User " << temp_user.user << " dropped and disconnected.\n";
                            break;
                        }
                    }
                    break;
                }
                else if(temp_user.is_operator && args[0]=="/SETPASS"){
                    if(args.size()<3){
                        send(Socket,"Error: wrong input format.\n",strlen("Error: wrong input format.\n"),MSG_NOSIGNAL);
                        continue;
                    }
                    int i=get_user_id(args[1]);
                    if(i==-1){
                        send(Socket,"Error: User not found\n",strlen("Error: User not found\n"),MSG_NOSIGNAL);
                        continue;
                    }
                    users_base_lock.lock();
                    strcpy(users_base[i].password,args[2].c_str());
                    users_base_lock.unlock();
                    send(Socket,"Success: User password successfully changed.\n",strlen("Success: User password successfully changed.\n"),MSG_NOSIGNAL);
		}
                else{
                    message temp_message;
                    temp_message.id=Socket;
                    temp_message.message=(string)temp_user.nickname+":"+command;
                    message_file.lock();
                    ofstream mfout;
                    mfout.open("public_messages",ios_base::app);
                    mfout << temp_message.message;
                    mfout.close();
                    message_file.unlock();
                    message_base_lock.lock();
                    message_base.push_back(temp_message);
                    message_base_lock.unlock();
                }
            }
            else{
                send(Socket,"Error: unknown command or you're not identified.Try /HELP for help.\n",strlen("Error: unknown command or you're not identified.Try /HELP for help.\n"),MSG_NOSIGNAL);
            }
            cout << "Username: " << temp_user.user << endl;
            for(auto x: args){
                cout << x << ' ';
            }
            cout << endl;
        }
    }

    disconnect(Socket,temp_user.nickname);
    return;
}


int main()
{
    user admin;
    admin.is_operator=true;
    strcpy(admin.user,"admin");
    strcpy(admin.nickname,"admin");
    strcpy(admin.password,"pass");
    strcpy(admin.last_visit,"Undefined.\n");

    users_base.push_back(admin);

    ifstream ufin("users");
    if(ufin.is_open()){
        user temp_user;
        string temp;
        vector<string>args;
        while(!ufin.eof()){
            memset(&temp_user,0,sizeof(temp_user));
            getline(ufin,temp);
            args=split_str_by_space(temp);
            if(args.size()!=4){
                continue;
            }
            strcpy(temp_user.user,args[0].c_str());
            strcpy(temp_user.nickname,args[1].c_str());
            strcpy(temp_user.password,args[2].c_str());
            if(args[3]=="1"){
                temp_user.is_operator=true;
            }
            strcpy(temp_user.last_visit,"A long time ago...\n");
            users_base.push_back(temp_user);
        }
        cout << "SYSTEM: Old users restored.\n";
    }
    else{
        cout << "SYSTEM: Warning, \'users\' file not found! New file will be created.\n";
    }


    int MasterSocket = socket(AF_INET,SOCK_STREAM,0);
    if(MasterSocket<0){
        cout << "SYSTEM: Error on socket creating.\n";
        return 9999;
    }
    struct sockaddr_in SockAddr;
    SockAddr.sin_family=AF_INET;
    SockAddr.sin_port=htons(5003);
    SockAddr.sin_addr.s_addr=htonl(INADDR_ANY);
    if(bind(MasterSocket, (struct sockaddr*)(&SockAddr),sizeof(SockAddr))<0){
        cout << "SYSTEM: Error on binding\n";
        return 9998;
    }
    listen(MasterSocket,MAX_CONNECTIONS);
    cout << "SYSTEM: Server started.\n";

    thread messenger(message_sender);
    messenger.detach();
    cout << "SYSTEM: Messenger started.\n";

    while(1){
        int SlaveSocket=accept(MasterSocket,0,0);
        cout << "SYSTEM: No." << SlaveSocket << " connected.\n";
        send(SlaveSocket,welcome,strlen(welcome),MSG_NOSIGNAL);
        thread connection(connected, SlaveSocket);
        clients_lock.lock();
        clients.push_back(SlaveSocket);
        clients_lock.unlock();
        connection.detach();
    }
    return 0;
}
