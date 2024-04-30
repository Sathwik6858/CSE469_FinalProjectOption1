#!/usr/bin/env python3
import sys
from blockchain import Blockchain
import argparse
def replaceshowcmds(args):
    args_string = ' '.join(args)
    args_string = args_string.replace('show cases', 'show_cases')
    args_string = args_string.replace('show items', 'show_items')
    args_string = args_string.replace('show history', 'show_history')
    return args_string.split()
def main():
    show_args = replaceshowcmds(sys.argv[1:])
    parser = argparse.ArgumentParser(description='Blockchain Chain of Custody Management System')
    parser.add_argument('action', choices=['add', 'checkout','checkin', 'show_cases', 'show_items', 'show_history' ,'remove', 'init', 'verify'], help='Action to perform on the blockchain')
    parser.add_argument('-i', '--item_id', nargs= '+', action= 'append', help='Item ID for the blockchain operation')
    parser.add_argument ('-c', '--case_id', help= 'Case ID for the blockchain operation')
    parser.add_argument('-g', '--creator', help='Creators identifier')
    parser.add_argument('-p', '--password', help='Password for blockchain verification')
    parser.add_argument('-n', '--numofentries', type=int, help='Used with show history to show number of entries')
    parser.add_argument('-y', '--why', help='Reason for Removal of evidence Item') # "--cmd" specifies to argeparse where to store input but also command can be ran like this for reason
    parser.add_argument('-r', '--reverse', action='store_true', help='Reverses the order of the block entries to show the most recent entries first')    
    args = parser.parse_args(show_args)
    args.r = args.reverse
    blockchain = Blockchain()
    if args.action == 'add':
        if not blockchain._check_for_initial():
            print("Initial Block Not Found")
            blockchain.init()
        else:
           duplicateId = False  
           if args.item_id and args.case_id:
                if args.password:
                    password_check = blockchain._verify_password(args.password, args.action)
                    if (password_check == False):
                        print("Invalid Password")
                        exit(1)
                    else:
                        for block in blockchain._read_blocks(True):
                            for item in args.item_id:
                                item = str(item)
                                item = item.replace("[", "").replace("]", "").replace("'", "")
                                if block['item_id'] == int((item)):
                                    print("Cant have duplicate IDS")
                                    duplicateId = True
                             
                        if not duplicateId :
                            for item in args.item_id:
                                item = str(item)
                                item = item.replace("[", "").replace("]", "").replace("'", "")
                                data = {"action": "add", "case_id": args.case_id, "item_id": str(item), "creator": args.creator}
                                outcome = blockchain.add_block(data)
                                if (outcome == True):
                                    print(f"Added item {item} from the blockchain.")
                                else: 
                                    print("Block add failed")
                        else:
                            exit(1) 
           else:
                print("Item/ Case ID is required for 'checkout' action.")
                exit(1)
    elif args.action == 'checkout':
         if args.item_id:
             if args.password:
                password_check = blockchain._verify_password(args.password, args.action)
                if (password_check == False):
                    print("Invalid Password")
                    exit(1)

                else:
                    itemerrorcheck = False
                    for block in blockchain._read_blocks(True):
                         for item in args.item_id:
                            item = str(item)
                            item = item.replace("[", "").replace("]", "").replace("'", "")
                            if ((block['item_id']) == int((item)) and block['state'] != 'CHECKEDIN') or block['state'] == 'INITIAL':
                                itemerrorcheck = True
                            elif (block['item_id']) == int((item)) and block['state'] == 'CHECKEDIN':
                                itemerrorcheck = False
                    if itemerrorcheck == True:
                        print("Items state must be checkin")
                        exit(1)
                    else:
                        checkoutflag = False
                        for block in blockchain._read_blocks(True):
                            if checkoutflag == True: 
                                break
                            for item in args.item_id:
                                item = str(item)
                                item = item.replace("[", "").replace("]", "").replace("'", "")
                                if (block['item_id']) == int((item)):
                                    data = {"action": "checkout", "item_id": str(item), "case_id": str(block['case_id']), "creator": block["creator"], "password": args.password}
                                    outcome = blockchain.add_block(data)
                                    if (outcome == True):
                                        print(f"Checked out item {args.item_id} from the blockchain.")
                                        checkoutflag = True
                                        break
    elif args.action == 'checkin':
        if args.item_id:
             if args.password:
                password_check = blockchain._verify_password(args.password, args.action)
                if (password_check == False):
                    print("Invalid Password")
                    exit(1)

                else:
                    itemerrorcheck = False
                    for block in blockchain._read_blocks(True):
                        for item in args.item_id:
                            item = str(item)
                            item = item.replace("[", "").replace("]", "").replace("'", "")
                            if (block['item_id']) == int((item)) and block['state'] == 'CHECKEDIN':
                                itemerrorcheck = True
                            if (block['item_id']) != int((item)) and block['state'] == 'INITIAL':
                                itemerrorcheck = True
                            elif block['state'] == 'CHECKEDOUT':
                                itemerrorcheck = False
                    if itemerrorcheck == True:
                        print("ERROR: Checkedin after Add")
                        exit(1)
                    else:
                        checkinflag = False
                        for block in blockchain._read_blocks(True):
                            if checkinflag == True:
                                break
                            for item in args.item_id:
                                item = str(item)
                                item = item.replace("[", "").replace("]", "").replace("'", "") #converting type list to string and then taking out the brackets
                                if (block['item_id']) == int((item)) and block['state'] == 'CHECKEDOUT': #we only want to checkin the corresponding block that has a state of checkedout
                                    data = {"action": "checkin", "item_id": str(item), "case_id": str(block['case_id']), "creator": block["creator"], "password": args.password}
                                    outcome = blockchain.add_block(data)
                                    if (outcome == True):
                                        print(f"Checked in item {item} from the blockchain.")
                                        checkinflag = True
                                        break
    elif args.action == 'show_history':
        pass
        if args.password:
                password_check = blockchain._verify_password(args.password, args.action)
                if (password_check == False):
                    print("Invalid Password")
                    exit(1)
                else:
                    if args.item_id:
                        num_of_cases = 0
                        current_numcase = 0
                        for block in blockchain._read_blocks(True):
                            for item in args.item_id:
                                item = str(item)
                                item = item.replace("[", "").replace("]", "").replace("'", "")
                                if (block['item_id']== int(item) and block['state'] != "INITIAL"):
                                   num_of_cases +=1

                        blockList = blockchain._read_blocks(True)
                        if args.r:
                            blockList = reversed(blockList)

                        for block in blockList:
                            for item in args.item_id:
                                item = str(item)
                                item = item.replace("[", "").replace("]", "").replace("'", "")
                                if (block['item_id']== int(item) and block['state'] != "INITIAL"): 
                                    current_numcase +=1
                                    print(f"Case: {block['case_id']}")
                                    print(f"Item: {block['item_id']}")
                                    print(f"Action:  {block['state']}")
                                    print(f"Time: {block['timestamp']}")
                                    if (current_numcase != num_of_cases):
                                        print("\n")
                                    else:
                                        pass
                    elif args.case_id:
                        num_of_cases = 0
                        current_numcase = 0
                        for block in blockchain._read_blocks(True):
                            if (str(block['case_id'])== args.case_id and block['state'] != "INITIAL"):
                                num_of_cases +=1
                        blockList = blockchain._read_blocks(True)
                        if args.r:
                            blockList = reversed(blockList)

                        for block in blockList:
                            pass                         
                            if str(block['case_id'])== args.case_id:
                                current_numcase +=1
                                print(f"Case: {block['case_id']}")
                                print(f"Item: {block['item_id']}")
                                print(f"Action:  {block['state']}")
                                print(f"Time: {block['timestamp']}")
                                if (current_numcase !=num_of_cases):
                                    print("\n")
                                else:
                                    pass
                    else:
                        current_numcase = 0
                        blockList = blockchain._read_blocks(True)
                        numOfEntries = len(blockList)
                        if type(args.numofentries) == int:
                            if args.numofentries <= numOfEntries:
                                numOfEntries =  args.numofentries
                        entryCount = 0
                        if args.r:
                            blockList = reversed(blockList)
                        for block in blockList:
                            if entryCount == numOfEntries:
                                break
                            current_numcase +=1
                            entryCount += 1
                            if block['state'] == "INITIAL":
                                print(f"Case: 00000000-0000-0000-0000-000000000000")
                                print(f"Item: 0")
                                print(f"Action:  {block['state']}")
                                print(f"Time: {block['timestamp']}")
                            else:
                                print(f"Case: {block['case_id']}")
                                print(f"Item: {block['item_id']}")
                                print(f"Action:  {block['state']}")
                                print(f"Time: {block['timestamp']}")
                            if (current_numcase != numOfEntries):
                                print("\n")
                            else:
                                pass
        else:
            decrypted_items = set()
            localcounter = 0
            globalcounter = 0
            num_of_cases = 0
            current_numcase = 0
            if args.item_id:
                for block in blockchain._read_blocks(True):
                        for item in args.item_id:
                            item = str(item)
                            item = item.replace("[", "").replace("]", "").replace("'", "")
                            localcounter+=1
                            if (block['item_id']== int(item) and block['state'] != "INITIAL"):
                                decrypted_items.add(localcounter)
                                num_of_cases+=1

                for block in blockchain._read_blocks(False):
                                globalcounter+=1
                                if (globalcounter in decrypted_items ):
                                    current_numcase+=1
                                    print(f"Case: {block['case_id']}")
                                    print(f"Item: {block['item_id']}")
                                    print(f"Action: {block['state']}")
                                    print(f"Time: {block['timestamp']}")
                                    if (current_numcase !=num_of_cases):
                                        print("\n")
                                    else:
                                        pass
    elif args.action == 'show_cases':
            caseset = set()
            for block in blockchain._read_blocks(True):
                if block['state'] != 'INITIAL' and block['case_id'] not in caseset:
                    print(block['case_id'])
                    caseset.add(block['case_id'])

    elif args.action == 'show_items':
            itemset = set()
            for block in blockchain._read_blocks(True):
                if block['state'] != 'INITIAL' and block['state']!='CHECKEDOUT' and str(block['case_id']) == args.case_id and block['item_id'] not in itemset:
                    print(block['item_id'])
                    itemset.add(block['item_id'])
    elif args.action == 'remove':
            itemerrorcheck = False
            for block in blockchain._read_blocks(True):
                for item in args.item_id:
                    item = str(item)
                    item = item.replace("[", "").replace("]", "").replace("'", "")
                    if ((block['item_id']) == int((item)) and block['state'] != 'CHECKEDIN') or block['state'] == 'INITIAL':
                        itemerrorcheck = True
                    elif (block['item_id']) == int((item)) and block['state'] == 'CHECKEDIN':
                        itemerrorcheck = False
            if itemerrorcheck == True:
                print("ERROR: Item to be removed doesnt have a Checkedin state")
                exit(1)
            else:

                if args.item_id and (args.why == 'RELEASED' or args.why=='DESTROYED' or args.why=='DISPOSED'):
                    args.item_id = str(args.item_id)
                    args.item_id = args.item_id.replace("[", "").replace("]", "").replace("'", "")
                    for block in blockchain._read_blocks(True): #find corresponding case_id to passed in item with checkedin state
                        if block['state'] == 'CHECKEDIN' and block['item_id'] == int(args.item_id):
                            data = {"action": "remove", "item_id": str(args.item_id), "creator": block["creator"], "password": args.password, "case_id": str(block['case_id']), "state": str(args.why)}
                            outcome = blockchain.add_block(data)
                            if (outcome == True):
                                print(f"Removed item {args.item_id} from the blockchain.")
                            else: 
                                print("Block remove failed")
                            break
                else:
                    print("Item ID/reason is required for 'remove' action.")
                    exit(1)
    elif args.action == 'init':
        blockchain.init()
    elif args.action == 'verify':
        blockchain._verify_checksums()
    else :
        print("invalid command")
if __name__ == "__main__":
    main()
