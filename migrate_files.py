#!/usr/bin/env python3
import json
import pickle


def save_json(data, file):
    with open(file, 'w') as fp:
        json.dump(data, fp)


def save_plain(data, file):
    with open(file, 'w') as fp:
        fp.write(data)


def save_binary(data, file):
    with open(file, 'wb') as fp:
        pickle.dump(data, fp)


def read_old_data(file):
    # old shit don't look!
    try:
        with open(file, 'r') as fp:
            data = eval(fp.read())
            return data

    except Exception as e:
        print(e)


def transfer_2_json(in_file, out_file):
    data = read_old_data(in_file)
    save_json(data, out_file)
    print(f"migrated: {in_file} to {out_file}")


def transfer_2_binary(in_file, out_file):
    data = read_old_data(in_file)
    save_binary(data, out_file)
    print(f"migrated: {in_file} to {out_file}")


def transfer_2_plain(in_file, out_file):
    data = read_old_data(in_file)
    save_plain(data, out_file)
    print(f"migrated: {in_file} to {out_file}")


def main():
    transfer_2_json('admins.dat', 'admins.json')
    transfer_2_json('greetings.dat', 'greetings.json')
    transfer_2_json('channels.dat', 'channels.json')
    transfer_2_json('ranch_milking_channels.dat', 'ranch_milking_channels.json')
    #transfer_2_plain('status.dat', 'status.txt')


if __name__ == "__main__":
    main()
