//
//  Hello World server in C++
//  Binds REP socket to tcp://*:5555
//  Expects "Hello" from client, replies with "World"
//


#include <string>
#include <iostream>
#include "zmq.hpp"
#include "json.hpp"
#ifndef _WIN32
#include <unistd.h>
#else
#include <windows.h>

#define sleep(n)	Sleep(n)
#endif

using namespace nlohmann;

void compute(json &j)
{
	auto data = j["data"];
	for (auto &pos: j["positions"])
	{
		auto frequency = data["frequency"].get<double>();
		auto offset = data["offset"].get<double>();
		auto amplitude = data["amplitude"].get<double>();
		auto envelope = data["envelope"].get<double>();
		auto x = pos[0].get<float>();
		auto y = pos[1].get<float>();
		float value = sin(x * frequency + offset) * amplitude * envelope;
		pos[1] = y + value;
	}
}

int main() {
	//  Prepare our context and socket
	zmq::context_t context(1);
	zmq::socket_t socket(context, ZMQ_REP);
	socket.bind("tcp://*:7070");

	while (true) {
		zmq::message_t request;

		//  Wait for next request from client
		socket.recv(&request);

		std::string request_s = std::string(static_cast<char*>(request.data()), request.size());
		//std::cout << "Received " << request_s << std::endl;
		auto j = json::parse(request_s.data());

		compute(j);

		//  Send reply back to client
		std::string dump = j["positions"].dump();
		zmq::message_t reply(dump.length());
		memcpy(reply.data(), dump.data(), dump.length());
		socket.send(reply);
	}
	return 0;
}