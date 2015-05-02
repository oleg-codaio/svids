/**
 * This is an example program used for proof-of-concept to demonstrate how svIDS
 * works.
 *
 * To understand what it does, suppose the following. You own a company that
 * provides high-performance computing services to clients, and provide a
 * control panel using a native Linux binary that can only be run off one
 * management node. Each customer has their own user account on this machine,
 * and you design a tool that lets customers query various information, such as
 * the quota or billing amount, as well as change various account settings.
 *
 * This sensitive data is located on the same machine, but you obviously want
 * to restrict access to it such that only the administrator can make changes
 * (such as increasing the quota) and users can only see their own information.
 * As a result, you place all the data files into a directory accessible only to
 * the root (0) user, and in your tool you set up <code>setuid(0)</code> so that
 * the tool runs with administrator privileges.
 *
 * The problem is that, with each coming week, your administrators keep adding
 * various features to the tool. You're worried that they might introduce a
 * vulnerability into the tool, allowing users to see others' sensitive account
 * information or, worse, modify their own quota and use up all your resources.
 *
 * Luckily, you have access to svIDS. You start by creating a .svids file with
 * all the expected normal inputs to your program, and svIDS records the
 * expected observations. Later on, when your program is actually running, svIDS
 * uses HMMs in order to monitor activity of every invocation of the tool. If
 * something looks suspicious--for instance, the tool is accessing directories
 * more often than it should or ones it seldom does (the admin directory with
 * all the secret settings)--then svIDS can interdict and terminate the program,
 * and notify you and the administrators immediately that something fishy is
 * going on.
 */

#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

void handleQuota(char* accountNo) {
    char buff[16];
    strcpy(buff, accountNo); // LOL.

    int acNo = atoi(buff);

    printf("Looking up account details for %d...\n", acNo);

    // TODO(oleg): implement the rest of the example. Essentially, this tool
    // would attempt to access the admin directory - if not accessed within the
    // last few hours, to retrieve some specific configuration. It would then
    // access the appropriate configuration file in a user-specific directory.

    // Note that there is a pretty obvious buffer overflow vulnerability in this
    // program. Even with such automatic defenses as stack canaries, address
    // space layout randomization, and data execution prevention, there are ways
    // of exploiting this program in order to gain access to the admin
    // directory; e.g., via a shell.

    // In theory, such access would involve an abnormal access to specific user
    // or administrator directories, and svIDS would be able to detect such an
    // intrusion and terminate this example tool.
}

int main(int argc, char** argv) {

    // Read arguments.
    if (argc != 3) {
        printf("usage: %s <command> <parameter>\n", argv[0]);
        return 1;
    }

    // Run as root so that we can access all the user data files.
    // Note: this binary has to be configured first. See
    // http://www.gnu.org/software/libc/manual/html_node/Setuid-Program-Example.html
    setuid(0);

    // Check what command the user wants to perform.
    if (!strcmp(argv[1], "quota")) {
        // Usage: quota <account number>
        handleQuota(argv[2]);
    } else {
        printf("Unknown command.\n");
        return 1;
    }

    return 0;
}

