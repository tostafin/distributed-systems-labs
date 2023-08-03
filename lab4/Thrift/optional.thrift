namespace cpp tutorial
namespace d tutorial
namespace dart tutorial
namespace java sr.hw
namespace php tutorial
namespace perl tutorial
namespace haxe tutorial

/* Based on https://github.com/zeroc-ice/ice-demos/blob/3.7/java/Ice/optional/Contact.ice */
enum NumberType {
    HOME = 0,
    OFFICE = 1,
    CELL = 2
}

struct Contact {
    1: string name,
    2: optional NumberType type,
    3: optional string number,
    4: optional i32 dialGroup
}

service ContactDB {
    void addContact(1: string name, 2: NumberType type, 3: string number, 4: i32 dialGroup),
    Contact query(1: string name),
    string queryNumber(1: string name)
}
