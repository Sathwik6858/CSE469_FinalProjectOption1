import ctypes
import os
import struct
from enum import Enum
from datetime import datetime, timezone
import hashlib
from uuid import UUID
from enum import Enum
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import sys

aes_key =  b"R0chLi4uLi4uLi4="
creator_password = os.getenv("BCHOC_PASSWORD_CREATOR", "C67C")
police_password = os.getenv("BCHOC_PASSWORD_POLICE", "P80P")
lawyer_password = os.getenv("BCHOC_PASSWORD_LAWYER", "L76L")
analyst_password = os.getenv("BCHOC_PASSWORD_ANALYST", "A65A")
executive_password = os.getenv("BCHOC_PASSWORD_EXECUTIVE", "E69E")
class State(Enum):
    INITIAL = "INITIAL"
    CHECKED_IN = "CHECKEDIN"
    CHECKED_OUT = "CHECKEDOUT"
    DISPOSED = "DISPOSED"
    DESTROYED = "DESTROYED"
    RELEASED = "RELEASED"
class Blockchain:
    RECORD_SIZE = 144
    def init(self):
        file_path = os.getenv("BCHOC_FILE_PATH", "C:\\Projects\\CSE469 Project\\CSE469\\chain.dat")
        if not os.path.isfile(file_path):
            self._write_starting_block()
        elif self._check_for_initial():
            print("Blockchain file found with INITIAL block.")
            self.previous_hash = self._get_last_hash()
        else:
            exit(1)

    def _write_starting_block(self):
        file_path = os.getenv("BCHOC_FILE_PATH", "C:\\Projects\\CSE469 Project\\CSE469\\chain.dat")
        try:
            with open(file_path, 'rb') as f:
                if f.read():
                    return
        except FileNotFoundError:
            print("Blockchain file not found.", end="")
            pass
            previous_hash = b'\x00' * 32
            timestamp = datetime.now(timezone.utc).timestamp()
            case_id = b"0" * 32
            item_id = b"0" * 32
            state = b'INITIAL\0\0\0\0\0'
            creator = b'\0' * 12
            owner = b'\0' * 12
            data = b"Initial block\0"
            data_length = 14
            block_format = '32s d 32s 32s 12s 12s 12s I {}s'.format(data_length)
            block_data = struct.pack(block_format, previous_hash, timestamp, case_id, item_id, state, creator, owner, data_length, data)
            with open(file_path, 'wb') as f:
                print(" Created INITIAL block.")
                f.write(block_data)

    def _read_blocks(self, decrypt_flag):
        file_path = os.getenv("BCHOC_FILE_PATH", "C:\\Projects\\CSE469 Project\\CSE469\\chain.dat")
        blocks = []
        try:
            with open(file_path, 'rb') as f:
                while True:
                    header_format = '32s d 32s 32s 12s 12s 12s I'
                    header_size = struct.calcsize(header_format)
                    header_data = f.read(header_size)
                    if not header_data:
                        break
                    try:
                        previous_hash, timestamp, case_id, item_id, state, creator, owner, data_length = struct.unpack(header_format, header_data)
                    except struct.error as e:
                        print("struct error")
                        exit(1)
                    data_format = '{}s'.format(data_length)
                    data = f.read(data_length)
                    data = struct.unpack(data_format, data)[0].decode('utf-8')
                    previous_hash = previous_hash.hex()
                    timestamp = datetime.utcfromtimestamp(timestamp)
                    timestamp = timestamp.isoformat() + 'Z'
                    if (decrypt_flag == True):
                        if case_id == b"0" * 32:
                            case_id = case_id.hex()[:32]
                            case_id = UUID(case_id)
                        else:
                            case_id = (case_id.decode())
                            case_id = bytes.fromhex(case_id)
                            case_id_decrypt = self._decrypt(case_id)
                            case_id_hex = (case_id_decrypt).hex()
                            case_id = UUID(case_id_hex)
                            
                        if item_id== b"0" * 32:
                            item_id = int.from_bytes(item_id, sys.byteorder)
                        else:
                            item_id = bytes.fromhex(item_id.decode())
                            item_id_decrypt = self._decrypt(item_id)
                            item_id = int.from_bytes(item_id_decrypt, "big")
                    else:
                        if case_id == b'\x00' * 32:
                            case_id = case_id.hex()[:32]
                            case_id = UUID(case_id)
                        else:
                            case_id = case_id.decode()
                        
                        if item_id == b'\x00' * 32:
                            item_id = int.from_bytes(item_id, sys.byteorder)
                        else: 
                            item_id = item_id.decode()
                    state = state.decode('utf-8').strip('\0')
                    creator = creator.decode('utf-8').strip('\0')
                    owner = owner.decode('utf-8').strip('\0')
                    blocks.append({
                        'previous_hash': previous_hash,
                        'timestamp': timestamp,
                        'case_id': case_id,
                        'item_id': item_id,
                        'state': state,
                        'creator': creator,
                        'owner': owner,
                        'data_length': data_length,
                        'data': data,
                        })
        except FileNotFoundError:
            print("Blockchain file not found.")
        return blocks
    def _get_specific_block(self, item_id):
        for block in reversed(self._read_blocks(True),):
            if block['item_id'] == item_id:
                return block
        return None
    def _verify_password(self, password, action):
        if action == "add":
            if (password != creator_password):
                return False
            else:
                return True
        elif action == "checkin" or "checkout":
            if (password != police_password and password!= lawyer_password and password !=executive_password and password != analyst_password):
                return False
            else:
                return True
    
    def _encrypt(self, data):
        cipher = AES.new(aes_key, AES.MODE_ECB)
        encrypted_data_bytes = cipher.encrypt(data)
        return encrypted_data_bytes
    
    def _decrypt(self, data):
        cipher = AES.new(aes_key, AES.MODE_ECB)
        decrypted_data = cipher.decrypt(data)
        return decrypted_data
        
    def _write_block(
            self,
            case_id: str,
            item_id: str,
            creator: str,
            state: str,
            owner: str,
            data: str,
            ):
        
        file_path = os.getenv("BCHOC_FILE_PATH", "C:\\Projects\\CSE469 Project\\CSE469\\chain.dat")
        case_idstr = case_id
        case_id_uuid = UUID(case_idstr) #converts the UUID string passed by user to UUID objects
        case_id_bytes = case_id_uuid.bytes
        encrypted_case_id_bytes = self._encrypt(case_id_bytes)
        encrypted_case_id_bytes = encrypted_case_id_bytes.hex().encode() #store as hex
        #convert 4 byte item_id and encrypt using AES ECB and store as a 32 byte hex
        item_id_int = int(item_id)
        item_id_bytes = item_id_int.to_bytes(16, byteorder = 'big')
        encrypted_item_id_bytes = self._encrypt(item_id_bytes)
        encrypted_item_id_bytes = encrypted_item_id_bytes.hex().encode() #encrypt as a hex bytes object
        creator_bytes = creator.ljust(12, '\x00').encode()
        state_bytes = state.ljust(12, '\x00').encode()
        owner_bytes = owner.ljust(12,'\x00').encode()
        data_bytes = data.encode()
        data_length = len(data_bytes)
        previous_hash = self._calculate_previous_hash(file_path)
        timestamp = datetime.utcnow().timestamp()
        block_format = '32s d 32s 32s 12s 12s 12s I {}s'.format(data_length)
        block_data = struct.pack(block_format, previous_hash, timestamp, encrypted_case_id_bytes, encrypted_item_id_bytes, state_bytes, creator_bytes, owner_bytes, data_length, data_bytes)
        try:
            with open(file_path, 'ab') as f:
                f.write(block_data)
            return True
        except Exception as e:
            print(f"Failed to write block: {e}")
            return False
        

    def add_block(self, data):
        action = data["action"]
        item_id = data["item_id"]
        creator = data.get("creator", '\0')
        case_id = data["case_id"]
        state = data.get("state", '\0')
        password = data.get("password", None)
        dat = ""
        owner = None

        if (action == "add"): 
            state = State.CHECKED_IN.value
            owner = '\0'
            outcome = self._write_block(case_id, item_id, creator, state, owner, dat)
            if (outcome == True):
                return True
            else: 
                return False
        elif (action == "remove"): 
            #block = self._get_specific_block(item_id) #get block that matches item_id
            #if (block and block["state"] == "CHECKEDIN"): 
                #creator = '\0'
                dat = ""
                owner = '\0'
                print(password)
                prevBlock = self._get_specific_block(item_id=int(item_id))
                if prevBlock != None:
                    owner = prevBlock['owner']
                outcome = self._write_block(case_id, item_id, creator, state, owner, dat)
                if (outcome == True):
                    return True
                else: 
                    return False
        elif(action =="checkout"):
            if password == police_password:
                owner = 'POLICE'
            elif password == analyst_password:
                owner = 'ANALYST'
            elif password == executive_password:
                owner = 'EXECUTIVE'
            elif password == lawyer_password:
                owner = 'LAWYER'
            state = State.CHECKED_OUT.value
            if owner != None:
                outcome = self._write_block(case_id, item_id, creator, state, owner, dat)
                if (outcome == True):
                    return True
                else: 
                    return False
            
        elif(action =="checkin"):
            print(password)
            if password == police_password:
                owner = 'POLICE'
            elif password == analyst_password:
                owner = 'ANALYST'
            elif password == executive_password:
                owner = 'EXECUTIVE'
            elif password == lawyer_password:
                owner = 'LAWYER'
            state = State.CHECKED_IN.value
            if owner!= None:
                outcome = self._write_block(case_id, item_id, creator, state, owner ,dat)
                if (outcome == True):
                    return True
                else: 
                    return False
            else:
                print("NOne owner")

        return None


    def _calculate_previous_hash(self, file_path):
        """
        Calculate the hash of the last block in the file
        """
        try:
            with open(file_path, 'rb') as f:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                if filesize == 0:
                    return b'\x00' * 32 #If the file is empty, return 32 bytes of zeros
                
                f.seek(-1, os.SEEK_END)
                while f.read(1) != b'\x00':
                    f.seek(-2, os.SEEK_CUR)
                    
                last_block_start = f.tell() + 1
                f.seek(last_block_start)
                last_block = f.read()

                #Calculate and return the hash
                return hashlib.sha256(last_block).digest()
            
        except FileNotFoundError:
            return b'\x00' * 32 #If the file does not exist, return 32 bytes of zeros
        
    def _check_for_initial(self):
        """
        Checks for an INITIAL block within the chain.
        :return: True if an INITIAL block is found, False otherwise.
        """
        # Use the _read_blocks method to get all blocks
        #blocks = self._read_blocks(True)

        # Iterate through each block and check its state
        for block in self._read_blocks(False):
            if block['state'] == 'INITIAL':
                return True  # Return True immediately if an INITIAL block is found

        # If the loop completes without finding an INITIAL block, return False
        return False

    def _calculate_block_hash(self, block):
        """
        Calculates the SHA-256 hash of the given block.
        :param block: A dictionary representing a block with keys for previous hash, timestamp,
                      case ID, item ID, state, and data.
        :return: A hex string representing the hash of the block.
        """
        # Create a string representation of the block.
        block_string = f"{block['previous_hash']}{block['timestamp']}{block['case_id']}{block['item_id']}{block['state']}{block['creator']}{block['owner']}{block['data_length']}{block['data']}"
    
        # Encode the string to a byte array
        block_encoded = block_string.encode()

        # Calculate the SHA-256 hash of the encoded block
        block_hash = hashlib.sha256(block_encoded).hexdigest()

        return block_hash

    def _verify_checksums(self):
        """
        Performs verification of the blockchain to check for integrity issues.
        :return: A tuple containing:
            - An integer: the number of blocks checked,
            - A string: error type ("NO PARENT", "DUPLICATE PARENT", "IMPROPER REMOVAL", or "VALID" if no errors),
            - A hash (or list of hashes in case of "DUPLICATE PARENT"): blocks involved in the error.
        """
        # Initially, assume blockchain is valid
        error = "CLEAN"
        error_hashes = []

        # Use the _read_blocks method to get all blocks
        blocks = self._read_blocks(False)

        # Dictionary to track parent blocks
        parent_blocks = {}

        for i, block in enumerate(blocks):
            # Skip the initial block as it has no parent
            if i == 0:
                prev_hash = block['previous_hash']
                current_hash = self._calculate_block_hash(block)
                parent_blocks[prev_hash] = current_hash
                continue

            prev_hash = block['previous_hash']
            current_hash = self._calculate_block_hash(block)  # You need to implement this method

            # Check for "NO PARENT"
            if prev_hash not in parent_blocks and i != 1:
                error = "NO PARENT"
                error_hashes.append(current_hash)
                exit(1)
                break

            # Check for "DUPLICATE PARENT"
            if prev_hash in parent_blocks:
                error = "DUPLICATE PARENT"
                error_hashes.extend([parent_blocks[prev_hash], current_hash])
                break

            parent_blocks[prev_hash] = current_hash

            # Additional checks can be implemented here, such as "IMPROPER REMOVAL", not usre how yet though
            #This might be a TODO

        # Determine the number of transactions (blocks) checked
        num_transactions = len(blocks)

        # Depending on your blockchain's structure, you may need to adjust how errors are detected and how hashes are calculated or stored.

        print ("Transactions in blockchain:", num_transactions)
        print("State of blockchain:", error)
        return num_transactions, error, error_hashes

    def _verify_remove_is_final(self):
        """
        Loops through the entire blockchain, keeping track of all items that have been removed. If an item that has been removed appears again, return False.
        Otherwise, return True.
        """
        # Use the _read_blocks method to get all blocks
        blocks = self._read_blocks(True)

        # Keep track of item IDs and their removal status
        removed_items = set()
        seen_items = set()

        for block in blocks:
            item_id = block['item_id']  # Assuming this gets the item ID correctly
            state = block['state']

            # Check if the item has been marked as removed
            if state in ["DISPOSED", "DESTROYED", "RELEASED"]:
                if item_id in removed_items:
                    # Item was removed before, should not appear again
                    continue  # might log a warning here. I have not implemented this yet though
                removed_items.add(item_id)

            if item_id in seen_items and item_id in removed_items:
                # If an item that was previously removed is seen again, return False
                return False
            else:
                seen_items.add(item_id)

        # If the loop completes without finding any items that reappear after removal, return True
        return True

    def _verify_add_is_first(self):
        """
        Loops through the entire blockchain, checking every new item. If a new item has the status 'CHECKEDIN', then continue. If a new item has any other status, return False.
        Once the end of the chain has been reached with no returns, return True.
        """
        # Use the _read_blocks method to get all blocks
        blocks = self._read_blocks(True)

        # Keep track of the item IDs that have been encountered
        encountered_items = {}

        for block in blocks:
            item_id = block['item_id']  # Assuming this gets the item ID correctly
            state = block['state']

            # Check if the item is encountered for the first time
            if item_id not in encountered_items:
                # If the item's first state is not 'CHECKEDIN', return False
                if state != 'CHECKEDIN':
                    return False
                encountered_items[item_id] = True
            # No need to check further if the item has already been encountered

        # If the loop completes without encountering any item that violates the rule, return True
        return True

    def _verify_all_released(self):
        """
        Loops through the blockchain, makes sure that the releases are valid
        """
        blocks = self._read_blocks(True)
        
        for block in blocks:
            if block['state'] == "RELEASED" and block['data_length'] <= 0:
                return False
            
        return True
    
    def _check_double_check(self):
        """
        Loops through the entire blockchain. Checks if any item is checked out twice 
        with no checkins inbetween, and if any item is checked in twice with no checkouts
        inbetween. Returns false if that does so happen to happen
        """
        # Use the _read_blocks method to get all blocks
        blocks = self._read_blocks(True)

        # Keep track of the last state for each item
        last_state = {}

        for block in blocks:
            item_id = block['item_id']  # Assuming this gets the item ID correctly
            state = block['state']

            # Check conditions for CHECKEDOUT and CHECKEDIN states
            if state == 'CHECKEDOUT':
                if item_id in last_state and last_state[item_id] == 'CHECKEDOUT':
                    # Item is checked out again without being checked in
                    return False
            elif state == 'CHECKEDIN':
                if item_id in last_state and last_state[item_id] == 'CHECKEDIN':
                    # Item is checked in again without being checked out
                    return False
        
            # Update the last state for the item
            last_state[item_id] = state

        # If the loop completes without finding any violations, return True
        return True
    
    def _unique_parent_check(self):
        """
        This checks if any block shares a parent with another and reutnrs false if it does
        """
        blocks = self._read_blocks(True)
        
        parents = []
        
        for block in blocks:
            parent = block['previous_hash']
            
            if parent in parents:
                return False
            else:
                parent.append(block['previous_hash'])
                
        return True

    def _get_last_block(self):
        """
        Retrieves the last block from the blockchain file.
        """
        file_path = os.getenv('BCHOC_FILE_PATH', 'default_blockchain_file_path.dat')
        blocks = self._read_blocks(False)

        if blocks:
            return blocks[-1]  # Return the last block if available
        else:
            return None  # Return None if the blockchain is empty

    def _get_last_hash(self):
        """
        Calculates hash of the last block, used when a previously created file is read.
        """
        # Use a modified version of _read_blocks method to get the last block only
        last_block = self._get_last_block()

        if last_block is None:
            return None  # Return None if there are no blocks
    
        last_block_hash = self._calculate_block_hash(last_block)

        return last_block_hash
